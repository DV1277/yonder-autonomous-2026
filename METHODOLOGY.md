# Methodology

Status: the applicant confirmed their review edits were finished and approved public publication of the AI-assisted project on October 9, 2026. The decisions below describe the implementation and measured runs. The review and assistance record is in `AI_LOG.md`.

## How to run

Core simulation and tests need Python 3.10+ and the standard library. Tested here on Python 3.12.1, macOS 15.7.7 arm64. From a fresh clone:

```bash
python3 -m unittest -v
python3 sim/launch.py --all
python3 sim/launch.py --scenario random --seed 42
python3 scripts/experiments.py
```

The tests currently contain 49 unchanged supplied cases and seven separate safety/state regressions. The all-scenario table must show every row REACHED with zero blocked ticks and zero needless replans. Extra tested seeds are 7, 19, 42, 101 and 223. Run logs are in `results/`; these finite checks do not guarantee every possible map.

To regenerate the short demo without opening any window:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-demo.txt
MPLBACKEND=Agg .venv/bin/python scripts/generate_demo.py
```

This uses pinned NumPy 2.4.1, Matplotlib 3.10.8 and Pillow 12.1.0. The core does not import them. The existing `demo/autonomous-demo.gif` is an 8.4-second replay of actual clean-sensor `goal-blocked` simulation at 4× playback. Its 42-frame manifest and final summary are beside it. `demo/stopped.png` and `demo/final.png` show stop/recovery behavior; no native UI or browser was used to make them.

## Implementation decisions

- Grid math uses floor, row/column order and cell centres from the supplied message contract. Circular centre-distance inflation makes a copied grid; the node separately blocks cells whose centres are too close to arena walls.
- A* uses a heap, octile distance and eight-connected moves with no corner cutting. Octile equals the unobstructed move cost and remains a lower bound when obstacles add detours. A blocked start may leave; a blocked goal has no route.
- Unknown cells are traversable because the goal lies outside the initial sensor footprint. Newly observed obstacles invalidate the remaining path before the rover reaches them. This policy depends on the provided look-ahead sensor and frequent updates; it is not a general safety guarantee for an unobserved physical environment.
- Replanning checks the suffix from one waypoint before the nearest point to include the current segment. Validation checks endpoints and samples segments at one-quarter cell spacing, with diagonal side checks. Obstacle changes behind the suffix do not trigger a replan.
- No route produces an explicit empty stop. Search retries after changed occupancy; an identical empty result is not published again. A cleared goal can therefore recover without keeping the old unsafe path active.
- Subscription QoS is BEST_EFFORT/VOLATILE, depth 1. Path publication is reliable. Monitoring uses the message's simulated timestamp and reports full published path length, replan count and elapsed simulated time since an actual replan. Stops/recoveries do not reset that replan age.

## Measured checks and limitations

The committed pre-run AI hypothesis predicted three boulders replans; the first measured run had 13, zero blocked and zero needless. Partial observations exposed more of each boulder on later ticks. The hypothesis remains in history and is attributed to AI assistance.

`python3 scripts/experiments.py` records three comparisons without editing production code or the simulator. Removing inflation stalls boulders with 150 blocked ticks. Blocking unknown cells stalls open with no route. On supplied tricky grid 223, Manhattan gives path cost 8.828427 versus octile's 8.242641. The diagnostic changes are process-local and restored afterward.

Part 1 assumes clean sensor observations. Confidence handling, Theta*, soft-cost planning and Webots were not implemented. The shim is not a deployed ROS robot integration. Goal coordinates/grid geometry are fixed by the supplied exercise; changing a goal while an existing path stays valid needs an additional goal-change trigger. Sampling validates the supplied grid-based A* paths, not arbitrary physical motion. The applicant reported five hours of their own project work/review for the submission's effort question.
