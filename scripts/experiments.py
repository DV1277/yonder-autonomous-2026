"""Required diagnostic comparisons; monkeypatches are process-local, not solution edits."""
import contextlib
import io
import json
import math
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "sim"))
from sim.launch import make_sim
import rclpy_lite as rclpy
import planner_node
import search
from grid_utils import Grid


def run(label, scenario, configure):
    old_inflate, old_astar = planner_node.inflate, planner_node.astar
    configure()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            sim = make_sim(scenario, 0, False)
            sim.run()
        return dict(label=label, scenario=scenario, result=sim.outcome,
                    ticks=sim.tick, blocked=sim.rover.blocked_ticks,
                    replans=sim.score.replans, needless=sim.score.needless)
    finally:
        planner_node.inflate, planner_node.astar = old_inflate, old_astar
        rclpy.shutdown()


def no_inflation():
    planner_node.inflate = lambda grid, radius: grid.copy()


def unknown_blocked():
    original = planner_node.astar
    planner_node.astar = lambda grid, start, goal, unknown_is_free: original(grid, start, goal, False)


def path_cost(path):
    return sum(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(path, path[1:]))


if __name__ == "__main__":
    records = [run("core", "boulders", lambda: None),
               run("without obstacle inflation", "boulders", no_inflation),
               run("unknown cells blocked", "open", unknown_blocked)]
    grid = Grid.from_ascii(["......", "......", "..#...", "#.....", "..##.#", "..#..."])
    original = search.heuristic
    good = path_cost(search.astar(grid, (0, 0), (5, 5)))
    try:
        search.heuristic = lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
        bad = path_cost(search.astar(grid, (0, 0), (5, 5)))
    finally:
        search.heuristic = original
    records.append(dict(label="heuristic comparison on supplied tricky grid 223",
                        octile_cost=good, manhattan_cost=bad,
                        note="Manhattan overestimates diagonal travel; production retains octile."))
    print(json.dumps(records, indent=2))
