# Track 82: CLI Contract Hardening and Stable Command Reference

**Status**: planned
**Dependencies**: Tracks 48, 49, 81
**Parallelization Node**: CLI Product Surface

## Phase 1: Contract Tests

- [ ] Task: Add failing tests for public command inventory, parser help, exit code behavior, and representative failure modes.
- [ ] Task: Add fixtures for commands that must support machine-readable JSON output.
- [ ] Task: Validate command-to-capability mapping against the Track 81 registry.
- [ ] Task: Identify commands that need clearer output, error, or deprecation behavior.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Contract Tests' (Protocol in workflow.md).

## Phase 2: CLI Hardening

- [ ] Task: Implement missing structured output modes for automation-facing commands.
- [ ] Task: Standardize exit codes and user-facing errors across CLI handlers.
- [ ] Task: Regenerate shell completion, manpage, and CLI reference docs from the live parser.
- [ ] Task: Add command deprecation guidance and compatibility rules to docs.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: CLI Hardening' (Protocol in workflow.md).

## Phase 3: Closeout and Mirror

- [ ] Task: Run focused CLI tests, docs generation checks, and relevant lint checks.
- [ ] Task: Verify CLI docs and generated references do not drift from the live parser.
- [ ] Task: Verify GitHub issue and project fields for Track 82.
- [ ] Task: Record CLI compatibility evidence and remaining intentional gaps.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md).
