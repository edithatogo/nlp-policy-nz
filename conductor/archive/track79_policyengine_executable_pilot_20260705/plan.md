# Track 79: PolicyEngine Executable Pilot

**Status**: planned
**Dependencies**: Tracks 7, 10, 11, 15, 20, 23, 27, 53, 74, 75, 77, 78
**Parallelization Node**: PolicyEngine Runtime Pilot

## Phase 1: Pilot Selection and Oracles

- [x] Task: Add failing tests for pilot-domain selection metadata and oracle fixture validation.
- [x] Task: Select one narrow reviewed domain and record source provisions, formulas, entities, periods, parameters, and expected outputs.
- [x] Task: Implement oracle fixture schema and fail-closed validation.
- [x] Task: Capture evidence explaining why this domain is suitable for the first executable pilot.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Pilot Selection and Oracles' (Protocol in workflow.md)

## Phase 2: PolicyEngine Generation

- [x] Task: Add failing tests for generated package layout and executable formula behavior.
- [x] Task: Implement PolicyEngine package generation for promoted pilot handoff artifacts.
- [x] Task: Preserve source provenance and review evidence in generated metadata.
- [x] Task: Add CLI/API entrypoint for deterministic package generation.
- [x] Task: Record a decision note covering PolicyEngine-first architecture and downstream ownership.
- [x] Task: Conductor - User Manual Verification 'Phase 2: PolicyEngine Generation' (Protocol in workflow.md)

## Phase 3: Execution Gate and Closeout

- [x] Task: Run focused PolicyEngine execution tests against oracle fixtures.
- [x] Task: Update docs with pilot usage, extension path, and fail-closed constraints.
- [x] Task: Verify `git diff --check`, focused tests, and relevant lint checks.
- [x] Task: Verify GitHub issue and project fields for Track 79.
- [x] Task: Archive the track after review fixes are applied.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Execution Gate and Closeout' (Protocol in workflow.md)
