# Track 76: All NZ Legislation Source Inventory

**Status**: planned
**Dependencies**: Tracks 4, 14, 23, 32, 54, 55
**Parallelization Node**: Full-Corpus Source Readiness

## Phase 1: Source Inventory Contract

- [x] Task: Add failing tests for inventory schema validation, stable citation paths, source checksums, and known-gap records. 7bba647
- [x] Task: Implement versioned inventory models and deterministic renderers. 7bba647
- [x] Task: Add fixture records for Acts, secondary legislation, amendments, commencement, repeals, redirects, and unavailable sources. 7bba647
- [x] Task: Document the source identity contract and whole-corpus claim boundary. 7bba647
- [x] Task: Capture evidence in the track folder, including fixture coverage and known live-source blockers. 7bba647
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Source Inventory Contract' (Protocol in workflow.md)

## Phase 2: Builder and CI Path

- [x] Task: Add failing tests for offline inventory builder behavior and optional live-probe skip behavior. 7bba647
- [x] Task: Implement the offline builder and optional live-probe entrypoint. 7bba647
- [x] Task: Wire a non-blocking or fixture-only CI validation path. 7bba647
- [x] Task: Emit deterministic inventory artifacts under `data/` or `artifacts/` with manifest metadata. 7bba647
- [x] Task: Record a decision note covering why live crawling is optional and how full-corpus promotion is proved. 7bba647
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Builder and CI Path' (Protocol in workflow.md)

## Phase 3: Closeout and Mirror

- [x] Task: Update docs and registry references for full-legislation source readiness. 7bba647
- [x] Task: Verify `git diff --check`, focused tests, and relevant lint checks. 7bba647
- [x] Task: Verify GitHub issue and project fields for Track 76. 7bba647
- [ ] Task: Archive the track after review fixes are applied.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md)
