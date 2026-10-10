# AI Usage Log

This log records AI assistance during implementation, debugging and verification. The applicant confirmed that their review edits were finished and authorized public publication on October 9, 2026. Entries 1–10 describe the work at each development stage; completed review and publication are recorded in entry 11.

## 1. Scaffold inspection and grid helpers

- Request: implement the Autonomous required core locally, preserve upstream files/tests, follow ordered commits, and document AI assistance honestly.
- Kept: upstream grid layout/docstrings and pure-function separation. Implemented floor-based world conversion, cell-centre conversion, and circular centre-distance inflation on a copied grid.
- Verification: read the original simulator messages/feed/rover/scoring; ran the open no-node baseline (STALLED, zero movement/path publications), then the supplied grid-helper suite.
- Errors caught: none observed in this step.

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

## 7. Scenario generalization

- Verification: all eight required table rows reached with 0 blocked and 0 needless. New seeds 7, 19, 42, 101 and 223 also reached, with 0 blocked/needless; full actual outputs are retained under `results/`.
- Kept: no seed-specific tuning or scenario-name branching. The planner imports no ground truth.

## 8. Monitoring correction during review

- Error caught in agent code review: `last_replan_stamp` was updated on initial, stop and recovery publications, so monitoring showed age since any plan rather than since an actual replan. The functional scoreboard counts were correct.
- Rewrote: update the replan timestamp only for a nonempty path replacing another nonempty path; label output `since_replan`. Initial output now says `never`.
- Verification: original plus added regressions rerun after the correction; scenario outcomes are unaffected because this changes monitoring state only.

## 9. Documentation and headless replay

- Request: prepare complete local core, actual evidence and a short demo; do not publish or submit.
- Kept: the required README answers and measured table, fresh-clone commands and documentation of AI assistance. At this stage, the write-up was prepared for applicant review.
- Rewrote during review: replay generation now refreshes its stopped snapshot on each invocation, using per-run state instead of an existing-file check.
- Verification: generated 42 frames from the actual goal-blocked simulation with Agg (no window/browser); inspected stopped/final PNGs locally and checked GIF duration/size. Final suite has 56 passing tests. Applicant review and public publication had not yet occurred at this stage; see entry 11 for their completion.
- Writing passes: reviewed the technical prose for direct explanations, accurate provenance and exact measured numbers, then provided the draft for applicant review.

## 10. Clean-checkout verification

- Cloned the completed local repository into a temporary directory inside this project, with no hardlinks. Ran the 56-case suite and required all-scenario table successfully from that checkout.
- Verified all 25 upstream simulator/provided-test files byte-for-byte against upstream commit `f59669408ed754b66b7eb93fb61807cf06c07726`.
- `results/verification.json` records the actual checkpoint time and elapsed wall-clock interval from local clone-directory creation (8.11 minutes at that checkpoint). This interval describes automated work; it is separate from the applicant's five reported hours in entry 11.

## 11. Applicant review and publication — October 9, 2026

- The applicant authorized implementation of the Autonomous project and used AI assistance to develop the required core, inspect results and correct bugs. The actual monitoring correction and replay-generation fix are documented in entries 8 and 9, with their verification. They were identified during AI-assisted code review.
- After receiving the local project and review materials, the applicant retained responsibility for reviewing the project and editing its attribution. The applicant then confirmed: “Edits finished; publish the reviewed project.” This approved publishing the reviewed code and documentation; it did not authorize submitting the application forms.
- The reviewed project was published at `https://github.com/DV1277/yonder-autonomous-2026`, with the original incremental development history. The first published main commit was `0879552914105552490a530e58586d07ae99e059`.
- For the project submission's effort question, the applicant directly reported five hours of their own work/review. That answer is separate from automated execution time and the brief's estimated duration.
- The applicant subsequently requested removal of the current “review pending” status and a clearer account of their approval and AI-assisted debugging. This documentation update records those confirmed decisions after publication. It leaves the original prediction, measured outcomes and historical commit sequence intact.
