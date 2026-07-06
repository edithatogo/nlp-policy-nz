# Track 82: CLI Contract Hardening and Stable Command Reference

## Overview

Harden the existing `nlp-policy-nz` command-line interface into a stable product surface. The CLI already exists; this track freezes command behavior, improves structured outputs, and adds tests and documentation that make future changes intentional.

## Functional Requirements

- Map every public CLI command to the Track 81 capability registry.
- Define command names, flags, positional arguments, defaults, output modes, and exit code behavior as a versioned contract.
- Add golden tests for help text, parser behavior, representative success paths, and common failure paths.
- Add structured JSON output support where downstream automation needs machine-readable results.
- Refresh shell completion and manpage/reference generation from the live parser.
- Document deprecation rules for command and flag changes.

## Non-Functional Requirements

- CLI tests must run without external credentials or heavyweight model downloads.
- Existing command names should remain backward compatible unless a clear deprecation path is documented.
- Error messages must be useful for local users and CI logs.
- Publishing commands must remain explicit and credential-gated.

## Acceptance Criteria

- [ ] Public CLI contract is documented and generated from the live parser or capability registry.
- [ ] Golden tests cover help text, command parsing, exit codes, JSON outputs, and failure paths.
- [ ] Commands map back to Track 81 capability IDs.
- [ ] Shell completion and manpage/reference docs are refreshed and validated in CI.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Replacing `argparse` with another CLI framework unless the Track 81 audit proves it is necessary.
- Changing core pipeline semantics.
- Adding new publishing destinations.
