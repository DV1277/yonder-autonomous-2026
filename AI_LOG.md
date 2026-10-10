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
