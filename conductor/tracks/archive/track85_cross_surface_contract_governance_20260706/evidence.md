# Track 85 Evidence

## Contract Artifacts

- `src/nlp_policy_nz/governance/interface_contract.py` builds the cross-surface conformance matrix and drift report.
- `src/nlp_policy_nz/contract_governance.py` exposes the release checklist and report writer used for governance artifacts.
- `scripts/check_interface_surface_contract.py` validates the Track 81 registry against the live CLI, API, SDK, and MCP surfaces.
- `docs/interface-contract-governance.md` documents the lifecycle, versioning, and release checklist rules.

## Verification

- `tests/test_track85_interface_surface_contract.py`
- `tests/test_contract_governance.py`
- `tests/test_surface_contracts.py`
- Static inspection of `src/nlp_policy_nz/governance/interface_contract.py` and `src/nlp_policy_nz/contract_governance.py`

## Closeout Notes

- Track 85 is implemented as deterministic governance and release automation around the already formalized interfaces.
- The repo intentionally keeps the checks local-first and credential-free.
- No Track 85-specific code fix was needed during review.
