"""
Planner node — your implementation goes here.

Run via:
    python sim/launch.py                       # default scenario
    python sim/launch.py --scenario open       # easiest world — start here
    python sim/launch.py --visualize           # with a live plot
    python sim/launch.py --all                 # every scenario, one summary table

This file uses rclpy_lite, a lightweight simulator shim that mirrors the real
rclpy (ROS 2 Python) API. The class names, method signatures, and message types
are identical to real ROS 2 — only the import paths differ:

    Real ROS 2:     import rclpy / from rclpy.node import Node
    This shim:      import rclpy_lite as rclpy / from rclpy_lite.node import Node

To run on a real ROS 2 system, swap the imports back to plain rclpy.

Division of labour
------------------
    grid_utils.py   grid maths (world <-> cell, inflating obstacles)     no ROS
    search.py       A*                                                    no ROS
    replan.py       "is my plan still valid? where am I on it?"           no ROS
    planner_node.py THIS FILE: receives grids, decides when to replan,
                    publishes paths, prints monitoring output              ROS glue

Get the three pure files passing their tests first. Then this file is mostly wiring.
"""

import rclpy_lite as rclpy
from rclpy_lite.node import Node
from rclpy_lite.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# Message types provided by the simulator
from sim.messages import GridSnapshot, make_path_msg

# Standard ROS message type (mirrored by the shim)
from nav_msgs.msg import Path

from grid_utils import Grid, inflate, path_length_m
from search import astar
from replan import next_waypoint_index, path_is_valid


class PlannerNode(Node):
    """ROS-style glue around pure planning helpers; Part 1 clean sensor policy."""

    def __init__(self):
        super().__init__("planner_node")
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                         durability=DurabilityPolicy.VOLATILE, depth=1)
        self.grid_sub = self.create_subscription(GridSnapshot, "/grid_feed", self.on_grid, qos)
        self.path_pub = self.create_publisher(Path, "/planned_path", 10)
        self.path_xy = None
        self.plan_count = 0
        self.replan_count = 0
        self.last_replan_stamp = None
        self.last_status_stamp = None
        self.failed_map = None
        self.reason = "initial"

    def on_grid(self, msg: GridSnapshot) -> None:
        grid = inflate(Grid.from_msg(msg), msg.robot_radius_m)
        # Walls are not marked by the feed. Enforce body clearance at arena edges.
        for row in range(grid.height):
            for col in range(grid.width):
                clearance = min(row + 0.5, col + 0.5,
                                grid.height - row - 0.5, grid.width - col - 0.5) * grid.resolution
                if clearance < msg.robot_radius_m:
                    grid.occupancy[grid.index(row, col)] = 100
        rover_xy = msg.rover_x, msg.rover_y
        goal_xy = msg.goal_x, msg.goal_y
        needed, self.reason = self.needs_replan(grid, rover_xy)
        if needed:
            previous = self.path_xy
            self.path_xy = self.plan(grid, rover_xy, goal_xy)
            if previous is None or self.path_xy != previous:
                self.publish_path(self.path_xy, msg.header.stamp)
                self.plan_count += 1
                if previous and self.path_xy:
                    self.replan_count += 1
                self.last_replan_stamp = msg.header.stamp
                self.last_status_stamp = None
            self.failed_map = tuple(grid.occupancy) if not self.path_xy else None
        self.print_status(msg.header.stamp)

    def needs_replan(self, grid: Grid, rover_xy) -> tuple:
        if self.path_xy is None:
            return True, "initial plan"
        if not self.path_xy:
            changed = tuple(grid.occupancy) != self.failed_map
            return changed, "map changed after no route" if changed else "waiting for route"
        index = max(0, next_waypoint_index(self.path_xy, rover_xy) - 1)
        if not path_is_valid(grid, self.path_xy, index):
            return True, "path blocked ahead"
        return False, "remaining path valid"

    def plan(self, grid: Grid, rover_xy, goal_xy):
        cells = astar(grid, grid.world_to_cell(*rover_xy),
                      grid.world_to_cell(*goal_xy), unknown_is_free=True)
        return [] if cells is None else [grid.cell_to_world(*cell) for cell in cells]

    def publish_path(self, points_xy, stamp: float) -> None:
        self.path_pub.publish(make_path_msg(points_xy, stamp))

    def print_status(self, stamp: float) -> None:
        if self.last_status_stamp is not None and stamp - self.last_status_stamp < 1.0 - 1e-9:
            return
        age = "never" if self.last_replan_stamp is None else f"{stamp - self.last_replan_stamp:.1f}s"
        print(f"[planner] t={stamp:.1f}s path={path_length_m(self.path_xy or []):.2f}m "
              f"replans={self.replan_count} since_plan={age} reason={self.reason}")
        self.last_status_stamp = stamp
