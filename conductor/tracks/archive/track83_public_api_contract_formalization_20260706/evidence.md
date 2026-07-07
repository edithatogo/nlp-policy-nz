# Track 83 Evidence

## Contract Artifacts

- `src/nlp_policy_nz/api/server.py` defines the public FastAPI surface, versioned OpenAPI generation, endpoint inventory, auth scopes, and RFC 7807 handling.
- `src/nlp_policy_nz/client/sync.py` and `src/nlp_policy_nz/client/async_client.py` expose the supported SDK surface and share the same route shapes.
- `docs-site/src/content/docs/api/openapi.json` and `docs-site/src/content/docs/api/openapi.md` provide the versioned API reference artifact.
- `docs/interface-contract-governance.md` and `docs/ops/api_security.md` document the API lifecycle and policy rules.

## Verification

- `tests/test_track83_api_contract.py`
- `tests/test_server.py`
- `tests/test_track46_production_hardening.py`
- Static inspection of `src/nlp_policy_nz/api/server.py`, `src/nlp_policy_nz/client/sync.py`, and `src/nlp_policy_nz/client/async_client.py`

## Closeout Notes

- Track 83 is already implemented in the repo as a versioned API contract layer on top of the Track 81 registry.
- The current workspace has unrelated environment issues for full test execution: the ad hoc Python runtime is missing `pytest` and `msgspec`, and `pyproject.toml` currently has a duplicate-value TOML parse error elsewhere in the tree.
- No Track 83-specific code fix was needed during review.
