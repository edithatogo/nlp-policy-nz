# Track 84 Evidence

## Contract Artifacts

- `src/nlp_policy_nz/mcp/server.py` defines the read-only MCP manifest, tools, resources, optional stdio entrypoint, and Track 81 capability mapping.
- `src/nlp_policy_nz/mcp/__init__.py` exposes the adapter surface as an optional package entrypoint.
- `tests/test_mcp_server.py` and `tests/test_surface_contracts.py` cover the manifest, resource payloads, and representative tool calls.
- `docs/interface-contract-governance.md` documents the adapter boundary, safety policy, and versioning rules.

## Verification

- `tests/test_mcp_server.py`
- `tests/test_surface_contracts.py`
- Static inspection of `src/nlp_policy_nz/mcp/server.py`

## Closeout Notes

- Track 84 is implemented as an optional, read-only MCP adapter rather than a business-logic layer.
- The repo already keeps mutating and external-network MCP capabilities out of scope.
- No Track 84-specific code fix was needed during review.
