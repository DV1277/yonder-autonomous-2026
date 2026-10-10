"""Additional safety/state regression tests; original supplied tests unchanged."""
import contextlib
import io
import unittest
from grid_utils import Grid
from replan import path_is_valid
from search import astar
from planner_node import PlannerNode
from sim.launch import make_sim
import rclpy_lite as rclpy


class AdditionalSafetyTests(unittest.TestCase):
    def test_diagonal_side_obstacle_invalidates_existing_path(self):
        grid = Grid.from_ascii(["..", ".#"])
        path = [grid.cell_to_world(0, 0), grid.cell_to_world(1, 1)]
        self.assertFalse(path_is_valid(grid, path))

    def test_obstacle_between_distant_waypoints(self):
        grid = Grid.from_ascii(["..#.."])
        self.assertFalse(path_is_valid(grid, [(0.5, 0.5), (4.5, 0.5)]))

    def test_empty_path_retries_only_on_changed_map(self):
        rclpy.init()
        node = PlannerNode()
        grid = Grid.from_ascii(["..."])
        node.path_xy = []
        node.failed_map = tuple(grid.occupancy)
        self.assertFalse(node.needs_replan(grid, (0.5, 0.5))[0])
        grid.occupancy[2] = 100
        self.assertTrue(node.needs_replan(grid, (0.5, 0.5))[0])
        rclpy.shutdown()

    def test_changed_obstacle_behind_is_ignored(self):
        rclpy.init()
        node = PlannerNode()
        grid = Grid.from_ascii([".........."])
        node.path_xy = [grid.cell_to_world(0, i) for i in range(10)]
        grid.occupancy[1] = 100
        self.assertFalse(node.needs_replan(grid, (7.5, 0.5))[0])
        rclpy.shutdown()

    def test_unknown_goal_needs_exploration_policy(self):
        grid = Grid.from_ascii(["..???"])
        self.assertIsNone(astar(grid, (0, 0), (0, 4), False))
        self.assertIsNotNone(astar(grid, (0, 0), (0, 4), True))

    def test_goal_stop_recovery_and_no_duplicate_empty_publications(self):
        with contextlib.redirect_stdout(io.StringIO()):
            sim = make_sim("goal-blocked", 0, False)
            sim.run()
        self.assertEqual(sim.outcome, "REACHED")
        self.assertEqual(sim.rover.blocked_ticks, 0)
        self.assertEqual(sim.score.needless, 0)
        kinds = [e.kind for e in sim.score.events]
        self.assertEqual(kinds.count("stop"), 1)
        self.assertEqual(kinds.count("recovery"), 1)
        self.assertEqual(sim.empty_paths_seen, 1)
        rclpy.shutdown()

    def test_open_node_does_not_replan_every_tick(self):
        with contextlib.redirect_stdout(io.StringIO()):
            sim = make_sim("open", 0, False)
            sim.run()
        self.assertEqual(sim.outcome, "REACHED")
        self.assertEqual(sim.paths_seen, 1)
        self.assertEqual(sim.score.replans, 0)
        self.assertEqual(sim.delivered_to_node(), sim.tick)
        rclpy.shutdown()
