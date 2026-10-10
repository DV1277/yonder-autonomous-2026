"""
A* search on a Grid — pure Python, NO ROS in this file.

    python -m unittest tests.test_search -v

Movement rules (fixed, so the tests can check them)
---------------------------------------------------
* 8-connected: a cell has up to 8 neighbours (up, down, left, right and the 4 diagonals).
* Cost of a move: 1.0 for up/down/left/right, sqrt(2) for a diagonal. (Cost is in
  cell-widths, not metres — multiply by grid.resolution if you need metres.)
* No corner cutting: a diagonal move is only allowed if BOTH of the two cells it
  squeezes between are passable. (A real rover cannot slip between two obstacles
  that touch at a corner.)
* Cells outside the grid don't exist.
"""

import heapq
import math
from itertools import count
from typing import List, Optional

from sim.grid_values import OCCUPIED, UNKNOWN

from grid_utils import Grid, Cell


def heuristic(a: Cell, b: Cell) -> float:
    """
    Estimate of the cost to travel from cell `a` to cell `b` on an EMPTY grid
    under the movement rules above.

    Choose and justify your choice in the README. The one hard requirement:
    it must NEVER OVERESTIMATE the true cost (that's what "admissible" means, and
    A* is only guaranteed to return the shortest path if it holds). The test
    checks this, and it is worth understanding why some very common heuristics
    fail it on an 8-connected grid.
    """
    dr, dc = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dr, dc) + (math.sqrt(2.0) - 1.0) * min(dr, dc)


def astar(grid: Grid, start: Cell, goal: Cell, unknown_is_free: bool = False) -> Optional[List[Cell]]:
    """
    Find the cheapest path from `start` to `goal`.

    Args:
        grid             the grid to search. OCCUPIED cells can't be entered.
        start, goal      (row, col) cells.
        unknown_is_free  how to treat UNKNOWN cells: True = passable, False = blocked.
                         Which is right for a rover that has only seen a small
                         circle of the world so far? Look at the very first tick
                         of a run before you decide.

    Returns:
        The path as a list of (row, col) cells, INCLUDING both start and goal, or
        None if there is no path. If start == goal, returns [start].

    Things to think about (the tests poke at each):
      * What if the goal is occupied?
      * The rover might already be standing on a cell that your obstacle
        inflation marked as blocked. Should search refuse to leave it?
      * Speed: a 100 x 100 grid must finish in well under a second. What data
        structure makes "give me the cheapest open node" fast?
    """
    def passable(cell):
        return (grid.in_bounds(*cell) and grid.get(*cell) != OCCUPIED
                and (unknown_is_free or grid.get(*cell) != UNKNOWN))

    if not grid.in_bounds(*start) or not grid.in_bounds(*goal):
        return None
    if start == goal:
        return [start]
    if not passable(goal):
        return None
    sequence = count()
    frontier = [(heuristic(start, goal), next(sequence), 0.0, start)]
    best = {start: 0.0}
    parent = {}
    while frontier:
        _, _, cost, cell = heapq.heappop(frontier)
        if cost > best.get(cell, math.inf):
            continue
        if cell == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return path[::-1]
        r, c = cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)):
            neighbor = r + dr, c + dc
            if not passable(neighbor):
                continue
            if dr and dc and (not passable((r + dr, c))
                              or not passable((r, c + dc))):
                continue
            candidate = cost + (math.sqrt(2.0) if dr and dc else 1.0)
            if candidate + 1e-12 < best.get(neighbor, math.inf):
                best[neighbor] = candidate
                parent[neighbor] = cell
                heapq.heappush(frontier, (candidate + heuristic(neighbor, goal),
                                         next(sequence), candidate, neighbor))
    return None
