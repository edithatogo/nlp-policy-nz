# CLI contract

This repository treats `nlp-policy-nz` as a stable argparse surface backed by the Track 81 capability registry in `src/nlp_policy_nz/cli/main.py`.

## Exit behavior

- Parse and usage errors return exit code `2`.
- `--help` returns exit code `0`.
- Runtime failures return exit code `1`.

## Structured output

- `search` defaults to JSON output and supports `--output-format text` for a human-readable summary.
- `quality validate` defaults to JSON output and supports `--output-format text`.
- `quality report` defaults to JSON output and supports `--output-format text`.
- JSON-emitting commands should keep field names stable and prefer additive changes.

## Compatibility rules

- Command names are stable unless a deprecation path is documented first.
- Flag removals require a documented replacement and a transition window.
- Generated completion and manpage output should be rebuilt from the live parser whenever the CLI changes.

## Capability registry

The public command inventory is mapped in `src/nlp_policy_nz/cli/main.py` via `CLI_CAPABILITIES` and attached to live parser objects as `cli_capability_id`.
