# Track 82 Evidence

## Contract Artifacts

- `src/nlp_policy_nz/cli/main.py` defines the live CLI capability registry, parser metadata, JSON output paths, and command-to-capability mapping.
- `src/nlp_policy_nz/cli/completion.py` renders shell completion and manpage text from the live parser and capability inventory.
- `docs/cli-contract.md` and `docs/interface-contract-governance.md` capture the CLI contract and compatibility guidance.

## Verification

- `tests/test_cli.py`
- `tests/test_surface_contracts.py`
- Static inspection of `src/nlp_policy_nz/cli/main.py` and `src/nlp_policy_nz/cli/completion.py`

## Closeout Notes

- Track 82 is implemented as a stable CLI contract layer on top of the Track 81 registry.
- The local ad hoc Python runtime in this workspace does not have `pytest` or `msgspec` installed, so I did not run a fresh end-to-end test pass here.
- Existing repository tests already cover the relevant parser, structured output, and completion/manpage behavior.
