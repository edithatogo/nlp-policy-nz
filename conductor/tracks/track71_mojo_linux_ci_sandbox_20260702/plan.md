# Track 71: Mojo Linux CI Sandbox

**Status**: planned
**Dependencies**: Track 70
**Parallelization Node**: Optional Linux Runtime Sandbox

## Phase 1: Sandbox Design

- [ ] Task: Confirm Track 70 readiness exit criteria are satisfied.
- [ ] Task: Choose one tiny deterministic sandbox kernel with Python reference behavior.
- [ ] Task: Define artifact parity checks for values, ordering, hashes, and error handling.
- [ ] Task: Document skip behavior for unsupported platforms.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Sandbox Design' (Protocol in workflow.md)

## Phase 2: CI Integration Plan

- [ ] Task: Add a Linux-only non-blocking CI path for the sandbox.
- [ ] Task: Keep Windows and default matrix jobs free of Mojo requirements.
- [ ] Task: Capture CI artifacts or logs proving install, execution, parity, and skip behavior.
- [ ] Task: Record a decision note confirming whether the sandbox remains useful enough for Track 72 benchmarking.
- [ ] Task: Record rollback steps for removing the sandbox.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: CI Integration Plan' (Protocol in workflow.md)

## Phase 3: GitHub and Conductor Closeout

- [ ] Task: Populate and verify the GitHub issue and project fields for Track 71.
- [ ] Task: Verify metadata status remains `planned` until implementation begins.
- [ ] Task: Confirm production code paths do not import or require Mojo.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: GitHub and Conductor Closeout' (Protocol in workflow.md)
