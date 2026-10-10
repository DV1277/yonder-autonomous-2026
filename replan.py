"""
Replan-trigger logic — pure Python, NO ROS in this file.

    python -m unittest tests.test_replan -v

The rover's view of the world changes every tick. A plan that was fine when you
made it may not be fine now — but re-running A* on every single tick is wasteful,
and the scoreboard counts it against you. These two functions are the building
blocks for "is my current plan still good, and where along it am I?".
"""

import math
from typing import Sequence

from grid_utils import Grid, Point


def next_waypoint_index(path_xy: Sequence[Point], rover_xy: Point) -> int:
    """
    Index of the waypoint in `path_xy` that is closest to the rover.

    Why you need it: the rover is somewhere along the path. Waypoints it has
    already passed can no longer hurt it. Only the part still AHEAD matters when
    you decide whether the path is still safe.

    Ties: return the lower index. `path_xy` is never empty when this is called.
    """
    if not path_xy:
        raise ValueError("path must be nonempty")
    return min(range(len(path_xy)),
               key=lambda i: (path_xy[i][0] - rover_xy[0]) ** 2
                           + (path_xy[i][1] - rover_xy[1]) ** 2)


def path_is_valid(grid: Grid, path_xy: Sequence[Point], start_index: int = 0) -> bool:
    """
    Is the part of the path from `start_index` onwards still safe to drive on?

    Args:
        grid         the CURRENT grid. (You decide whether to pass in an inflated
                     one — think about which you want.)
        path_xy      the plan, as (x, y) points in WORLD coordinates.
        start_index  only waypoints from this index onwards are checked.

    Returns False if any checked waypoint is in an OCCUPIED cell or outside the
    grid. Also False for an empty path (there is nothing to follow).

    Why the path is stored in world coordinates and not as cells: a cell index
    only means something relative to one particular grid. Points in the world
    keep their meaning when the grid changes.
    """
    if not path_xy or start_index < 0 or start_index >= len(path_xy):
        return False

    def clear(cell):
        return grid.in_bounds(*cell) and not grid.is_occupied(*cell)

    points = path_xy[start_index:]
    if not all(clear(grid.world_to_cell(*point)) for point in points):
        return False
    # Validate segments too: fresh obstacles can invalidate a diagonal side cell
    # or land between distant waypoints even when both endpoints remain free.
    for a, b in zip(points, points[1:]):
        steps = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1])
                                 / (grid.resolution * 0.25)))
        previous = grid.world_to_cell(*a)
        for i in range(1, steps + 1):
            t = i / steps
            cell = grid.world_to_cell(a[0] + t * (b[0] - a[0]),
                                      a[1] + t * (b[1] - a[1]))
            if not clear(cell):
                return False
            if cell[0] != previous[0] and cell[1] != previous[1]:
                if not clear((cell[0], previous[1])) or not clear((previous[0], cell[1])):
                    return False
            previous = cell
    return True
