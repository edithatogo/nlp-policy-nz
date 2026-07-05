# Track 80: OpenFisca and Multi-Engine Parity

**Status**: planned
**Dependencies**: Tracks 46, 50, 52, 78, 79
**Parallelization Node**: Multi-Engine Rules-as-Code Validation

## Phase 1: Engine Adapter Contract

- [ ] Task: Add failing tests for engine adapter metadata, optional dependency behavior, and support-level reporting.
- [ ] Task: Define a generic rules-engine adapter contract for PolicyEngine, OpenFisca, and future engines.
- [ ] Task: Document dependency isolation, skip behavior, and GitHub Actions compatibility.
- [ ] Task: Capture evidence for adapter validation and dependency boundaries.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Engine Adapter Contract' (Protocol in workflow.md)

## Phase 2: OpenFisca Export and Parity

- [ ] Task: Add failing tests for OpenFisca package export from promoted pilot handoff artifacts.
- [ ] Task: Implement OpenFisca-compatible package generation for the pilot domain.
- [ ] Task: Add parity tests comparing PolicyEngine and OpenFisca outputs against oracle fixtures.
- [ ] Task: Emit deterministic parity reports with source IDs, engine versions, outputs, and known gaps.
- [ ] Task: Record a decision note covering when additional engines should be onboarded.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: OpenFisca Export and Parity' (Protocol in workflow.md)

## Phase 3: Closeout and Mirror

- [ ] Task: Update docs with engine support levels, parity workflow, and extension criteria.
- [ ] Task: Verify `git diff --check`, focused tests, and relevant lint checks.
- [ ] Task: Verify GitHub issue and project fields for Track 80.
- [ ] Task: Archive the track after review fixes are applied.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md)
