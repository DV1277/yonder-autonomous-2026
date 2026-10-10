# AI Usage Log

This project is being implemented by Codex (GPT-6.1 Sol), with the applicant's explicit authorization. Applicant review and understanding are pending. Entries describe actual agent work; they are not invented accounts of the applicant independently coding or discovering bugs.

## 1. Scaffold inspection and grid helpers

- Request: implement the Autonomous required core locally, preserve upstream files/tests, follow ordered commits, and document AI assistance honestly.
- Kept: upstream grid layout/docstrings and pure-function separation. Implemented floor-based world conversion, cell-centre conversion, and circular centre-distance inflation on a copied grid.
- Verification: read the original simulator messages/feed/rover/scoring; ran the open no-node baseline (STALLED, zero movement/path publications), then the supplied grid-helper suite.
- Errors caught: none observed in this step; do not invent an AI mistake for the log.

## 2. A* search

- Kept: heap frontier, octile heuristic, eight-connected moves, explicit no-corner-cut checks, permissive blocked start but blocked goal rejection.
- Verification: supplied search suite checks optimality, unknown-cell policy, corner cutting, blocked-start escape and 150×150 performance.
- Errors caught: none in this step. The overestimating-heuristic comparison is reserved for a separately labeled diagnostic, not production code.

## 3. Replan helpers

- Kept: nearest waypoint with stable lower-index ties, world-coordinate path validation, and segment/corner checks beyond endpoint checks.
- Verification: supplied replan suite; later separate added regression tests cover newly blocked diagonal sides and obstacles between distant endpoints.
- Errors caught: none observed in this step; stronger segment validation is an intentional safety choice.

## 4. Plan-once node wiring

- Kept: BEST_EFFORT/VOLATILE sensor subscription, reliable path publication, unknown-as-traversable exploration, explicit arena-wall clearance, simulation-stamp monitoring.
- Verification: required open scenario with one initial plan, no replan and no blocked ticks. No boulders scenario has run at this stage.
- Current staged limitation: this commit plans once only; map-change replanning follows in step 6.

## 5. Prediction and selective replanning

- The required standalone `prediction: boulders` README commit was made before the first boulders execution. It explicitly attributes the three-replan hypothesis to AI assistance; it is not fabricated applicant testimony.
- Kept: validate only the remaining path (nearest waypoint minus one for current segment coverage); recompute after invalidation; publish an explicit empty stop if no route; retry failed search only after occupancy changes; suppress duplicate empty publications.
- Verification: first boulders and wall runs are recorded in `results/step6-*.txt`; compare actual scoreboard to the pre-run hypothesis.

- Actual first boulders result: goal reached in 124 ticks, 13 replans, 0 blocked, 0 needless. The three-replan hypothesis was wrong: successive partial observations of each boulder caused multiple legitimate invalidations. Wall also reached the goal with 0 blocked and 0 needless (17 replans). No result was retroactively relabeled as a prediction.

## 6. Dynamic scenarios

- Verification: popup reaches in 130 ticks with 3 replans; its behind-rover event at tick 80 produces no path event. Goal-blocked reaches in 166 ticks; empty stop at 104, recovery at 144, 0 blocked/needless in both runs.
- Kept: empty-publication suppression and occupancy-change recovery worked without modification. No simulated success was invented and no supplied tests/worlds were edited.
