# Track 71: Mojo Linux CI Sandbox

**Status**: completed
**Dependencies**: Track 70
**Parallelization Node**: Optional Linux Runtime Sandbox

## Phase 1: Sandbox Design

- [x] Task: Confirm Track 70 readiness exit criteria are satisfied. Evidence: Track 70 archive decision and Stage 2 roadmap alignment.
- [x] Task: Choose one tiny deterministic sandbox kernel with Python reference behavior. Evidence: `experiments/mojo/kernel.mojo` and `experiments/mojo/sandbox.py`.
- [x] Task: Define artifact parity checks for values, ordering, hashes, and error handling. Evidence: deterministic JSON payload comparison in `tests/test_track71_mojo_sandbox.py`.
- [x] Task: Document skip behavior for unsupported platforms. Evidence: `docs/mojo_sandbox.md`.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Sandbox Design' (Protocol in workflow.md)

## Phase 2: CI Integration Plan

- [x] Task: Add a Linux-only non-blocking CI path for the sandbox. Evidence: `.github/workflows/ci.yml`.
- [x] Task: Keep Windows and default matrix jobs free of Mojo requirements. Evidence: workflow guard limits the sandbox job to Ubuntu + Python 3.12.
- [x] Task: Capture CI artifacts or logs proving install, execution, parity, and skip behavior. Evidence: JSON report rendering and kernel parity check in CI step plus local pytest coverage.
- [x] Task: Record a decision note confirming whether the sandbox remains useful enough for Track 72 benchmarking. Evidence: `conductor/mojo-migration-roadmap.md` Stage 3 promotion threshold.
- [x] Task: Record rollback steps for removing the sandbox. Evidence: `docs/mojo_sandbox.md`.
- [x] Task: Conductor - User Manual Verification 'Phase 2: CI Integration Plan' (Protocol in workflow.md)

## Phase 3: GitHub and Conductor Closeout

- [x] Task: Populate and verify the GitHub issue and project fields for Track 71. Evidence: issue `#78` and Projects `#3` and `#4`.
- [x] Task: Verify metadata status remains `planned` until implementation begins. Evidence: metadata was `planned` during implementation and is archived now that closeout is complete.
- [x] Task: Confirm production code paths do not import or require Mojo. Evidence: sandbox code stays under `experiments/mojo/` and the main package path is unchanged.
- [x] Task: Conductor - User Manual Verification 'Phase 3: GitHub and Conductor Closeout' (Protocol in workflow.md)

## Evidence

- `pixi run python -m pytest -p no:tach tests/test_track71_mojo_sandbox.py -q`
- `pixi run python -m py_compile experiments/__init__.py experiments/mojo/__init__.py experiments/mojo/sandbox.py tests/test_track71_mojo_sandbox.py`
- `.github/workflows/ci.yml` adds the Linux-only, non-blocking Mojo sandbox job.
