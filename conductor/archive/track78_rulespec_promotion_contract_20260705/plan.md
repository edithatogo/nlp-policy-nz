# Track 78: RuleSpec Promotion Contract

**Status**: planned
**Dependencies**: Tracks 27, 54, 55, 76, 77
**Parallelization Node**: Reviewed RuleSpec Handoff

## Phase 1: Promotion Schema

- [x] Task: Add failing tests for RuleSpec promotion states and fail-closed validation.
- [x] Task: Implement promotion payload models and validators.
- [x] Task: Add fixture handoffs for promoted, rejected, deferred, and blocked candidates.
- [x] Task: Document required reviewer evidence and oracle references.
- [x] Task: Capture evidence for validation failures and accepted handoff payloads.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Promotion Schema' (Protocol in workflow.md)

## Phase 2: Downstream Handoff

- [x] Task: Add failing tests for RuleSpec handoff rendering and source-verification compatibility.
- [x] Task: Implement deterministic JSON/YAML handoff export for `rulespec-nz`.
- [x] Task: Add docs explaining repository ownership boundaries and downstream runtime responsibilities.
- [x] Task: Record a decision note covering why executable semantics remain downstream.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Downstream Handoff' (Protocol in workflow.md)

## Phase 3: Closeout and Mirror

- [x] Task: Update README/docs with RuleSpec promotion workflow.
- [x] Task: Verify `git diff --check`, focused tests, and relevant lint checks.
- [x] Task: Verify GitHub issue and project fields for Track 78.
- [x] Task: Archive the track after review fixes are applied.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md)
