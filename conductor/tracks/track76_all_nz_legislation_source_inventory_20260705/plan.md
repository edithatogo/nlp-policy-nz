# Track 76: All NZ Legislation Source Inventory

**Status**: planned
**Dependencies**: Tracks 4, 14, 23, 32, 54, 55
**Parallelization Node**: Full-Corpus Source Readiness

## Phase 1: Source Inventory Contract

- [ ] Task: Add failing tests for inventory schema validation, stable citation paths, source checksums, and known-gap records.
- [ ] Task: Implement versioned inventory models and deterministic renderers.
- [ ] Task: Add fixture records for Acts, secondary legislation, amendments, commencement, repeals, redirects, and unavailable sources.
- [ ] Task: Document the source identity contract and whole-corpus claim boundary.
- [ ] Task: Capture evidence in the track folder, including fixture coverage and known live-source blockers.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Source Inventory Contract' (Protocol in workflow.md)

## Phase 2: Builder and CI Path

- [ ] Task: Add failing tests for offline inventory builder behavior and optional live-probe skip behavior.
- [ ] Task: Implement the offline builder and optional live-probe entrypoint.
- [ ] Task: Wire a non-blocking or fixture-only CI validation path.
- [ ] Task: Emit deterministic inventory artifacts under `data/` or `artifacts/` with manifest metadata.
- [ ] Task: Record a decision note covering why live crawling is optional and how full-corpus promotion is proved.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Builder and CI Path' (Protocol in workflow.md)

## Phase 3: Closeout and Mirror

- [ ] Task: Update docs and registry references for full-legislation source readiness.
- [ ] Task: Verify `git diff --check`, focused tests, and relevant lint checks.
- [ ] Task: Verify GitHub issue and project fields for Track 76.
- [ ] Task: Archive the track after review fixes are applied.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md)
