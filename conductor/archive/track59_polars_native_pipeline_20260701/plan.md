# Track 59: Polars-Native Corpus Pipeline Substitution

**Status**: completed
**Dependencies**: Tracks 6, 23, 32, 55, 56
**Parallelization Node**: Runtime Modernization

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Inventory the current corpus-browser hot paths and define the pandas/Polars boundary | [x] ade3fa2 | conductor_orchestrator |
| 2 | Implement a Polars-native storage/search/stats core behind stable wrappers in `spaces/app.py` | [x] ade3fa2 | conductor_orchestrator |
| 3 | Add a benchmark harness that compares pandas baseline timings against the Polars candidate paths | [x] ade3fa2 | conductor_orchestrator |
| 4 | Add parity tests and regression tests for the new Polars core and the public pandas boundary | [x] ade3fa2 | conductor_orchestrator |
| 5 | Update the dependency policy matrix and supporting docs with the dataframe surface decision | [x] ade3fa2 | conductor_orchestrator |
| 6 | Sync the Conductor registry, GitHub issue mirror, and GitHub Projects | [x] ade3fa2 | conductor_orchestrator |
| 7 | Capture validation evidence, mark the track complete, and record the final commit hashes | [x] ade3fa2 | conductor_orchestrator |

## Evidence Notes

Track 59 is intentionally local-first and CI-friendly. The benchmark path uses
fixture-sized data so GitHub Actions can exercise the same code paths without a
full corpus. The public app continues to expose pandas objects while the
internal hot path is shifted to Polars.
