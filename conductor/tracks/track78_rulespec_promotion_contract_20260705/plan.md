# Track 78: RuleSpec Promotion Contract

**Status**: planned
**Dependencies**: Tracks 27, 54, 55, 76, 77
**Parallelization Node**: Reviewed RuleSpec Handoff

## Phase 1: Promotion Schema

- [ ] Task: Add failing tests for RuleSpec promotion states and fail-closed validation.
- [ ] Task: Implement promotion payload models and validators.
- [ ] Task: Add fixture handoffs for promoted, rejected, deferred, and blocked candidates.
- [ ] Task: Document required reviewer evidence and oracle references.
- [ ] Task: Capture evidence for validation failures and accepted handoff payloads.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Promotion Schema' (Protocol in workflow.md)

## Phase 2: Downstream Handoff

- [ ] Task: Add failing tests for RuleSpec handoff rendering and source-verification compatibility.
- [ ] Task: Implement deterministic JSON/YAML handoff export for `rulespec-nz`.
- [ ] Task: Add docs explaining repository ownership boundaries and downstream runtime responsibilities.
- [ ] Task: Record a decision note covering why executable semantics remain downstream.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Downstream Handoff' (Protocol in workflow.md)

## Phase 3: Closeout and Mirror

- [ ] Task: Update README/docs with RuleSpec promotion workflow.
- [ ] Task: Verify `git diff --check`, focused tests, and relevant lint checks.
- [ ] Task: Verify GitHub issue and project fields for Track 78.
- [ ] Task: Archive the track after review fixes are applied.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md)
