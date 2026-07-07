# Track 81 Evidence

## Contract Artifacts

- `src/nlp_policy_nz/interface_contract.py` defines the machine-readable interface contract, capability validation, and surface inventory.
- `src/nlp_policy_nz/cli/main.py` exposes the CLI capability registry and command metadata.
- `src/nlp_policy_nz/api/server.py` exposes the public HTTP endpoint inventory and versioned API contract metadata.
- `src/nlp_policy_nz/mcp/server.py` exposes the read-only MCP manifest and tool inventory.
- `src/nlp_policy_nz/contract_governance.py` and `src/nlp_policy_nz/governance/interface_contract.py` provide the adapter gap and conformance report layers.

## Documentation

- `docs/capabilities.md`
- `docs/cli-contract.md`
- `docs/interface-contract-governance.md`

## Verification

- `pixi run pytest tests/test_interface_contract.py tests/test_surface_contracts.py tests/test_contract_governance.py tests/test_cli.py tests/test_server.py -q`
- `pixi run python scripts/check_interface_surface_contract.py --format markdown`

## Closeout Notes

- The registry snapshot and live surfaces are aligned.
- Adapter gaps are recorded as follow-on work for later tracks.
- GitHub issue and project mirror were already populated for this track before archive closeout.
