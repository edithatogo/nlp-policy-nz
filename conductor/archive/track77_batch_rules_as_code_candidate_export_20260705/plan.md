# Track 77: Batch Rules-as-Code Candidate Export

**Status**: planned
**Dependencies**: Tracks 10, 11, 12, 14, 15, 18, 26, 27, 54, 55, 56, 76
**Parallelization Node**: Rules-as-Code Candidate Generation

## Phase 1: Batch Contract

- [x] Task: Add failing tests for batch RAC candidate schema, deterministic ordering, and source trace preservation.
- [x] Task: Define batch export models that connect source inventory, extraction manifests, and existing RAC bridge records.
- [x] Task: Add fixture inputs spanning obligations, permissions, prohibitions, thresholds, dates, exceptions, and known gaps.
- [x] Task: Document the candidate/export boundary and non-executable status.
- [x] Task: Capture evidence for schema stability and source trace coverage.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Batch Contract' (Protocol in workflow.md)

## Phase 2: CLI and API Export

- [x] Task: Add failing CLI/API tests for batch RAC export.
- [x] Task: Implement batch export entrypoints with fixture-first defaults.
- [x] Task: Emit extraction manifest JSON and JSON-LD bridge bundles.
- [x] Task: Add known-gap and review-status propagation.
- [x] Task: Record a decision note covering candidate confidence, review status, and executable-rule boundaries.
- [x] Task: Conductor - User Manual Verification 'Phase 2: CLI and API Export' (Protocol in workflow.md)

## Phase 3: Closeout and Mirror

- [x] Task: Update README/docs with batch RAC export usage.
- [x] Task: Verify `git diff --check`, focused tests, and relevant lint checks.
- [x] Task: Verify GitHub issue and project fields for Track 77.
- [x] Task: Archive the track after review fixes are applied.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md)
