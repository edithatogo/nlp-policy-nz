# Track 63: nlprule Grammar and Rule Matching Evaluation

**Status**: planned
**Dependencies**: Tracks 3, 10, 13, 23, 55
**Parallelization Node**: Rust-Backed Rule Matching

## Phase 1: Rule Matching Evaluation Surface

- [x] Task: Register Track 63 in `conductor/tracks.md` with the correct
  dependency and phase metadata.
- [x] Task: Add a deterministic grammar-matching evaluator with optional
  nlprule availability detection and a spaCy fallback.
- [x] Task: Add tests for obligation, prohibition, deadline, and Te Reo Māori
  token preservation behavior.
- [x] Task: Map grammar matches into the existing extraction and quality
  schemas.
- [x] Task: Record the adoption decision and rollback note for nlprule.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Rule Matching
  Evaluation Surface' (Protocol in workflow.md)

## Phase 2: Closeout

- [x] Task: Verify the local metadata, spec, plan, and index parse correctly.
- [x] Task: Verify the GitHub issue and project rows reflect the implemented
  track state.
- [x] Task: Run focused tests and `git diff --check`.
- [x] Task: Mark Track 63 complete in the tracks registry and commit the
  implementation.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Closeout' (Protocol
  in workflow.md)
