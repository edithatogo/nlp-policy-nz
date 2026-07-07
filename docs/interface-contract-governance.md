# Interface Contract Governance

Track 85 keeps the public CLI, HTTP API, Python SDK, and future MCP surfaces aligned to the checked-in Track 81 registry.

## Source of Truth

- Registry snapshot: `data/track81/interface_surface_registry.json`
- CI check: `scripts/check_interface_surface_contract.py`
- Python API: `src/nlp_policy_nz/governance/interface_contract.py`

The registry is the contract. Surface code, documentation, and release notes should follow it, not redefine it.

## Surface Policy

- CLI commands should remain thin adapters over core modules.
- HTTP routes should validate input, call core functions, and return stable response models.
- The SDK should mirror the public API and avoid bespoke business logic.
- MCP is a read-only surface today. Its tools and resources must stay thin adapters over core helpers, and any mutating or external-network tool stays out of scope until a new contract version explicitly approves it.

## Versioning And Deprecation

- Capability IDs are stable once published.
- Adding a public capability requires a registry update, a docs update, and a conformance run.
- Changing a request or response shape requires a version review and a release note.
- Removing a capability requires a deprecation window, a registry change, and a new conformance pass.
- MCP tools and resources inherit the same versioning and deprecation rules as CLI, API, and SDK exposures.

## Release Checklist

1. Refresh the registry snapshot.
2. Run `scripts/check_interface_surface_contract.py`.
3. Regenerate or validate CLI, OpenAPI, SDK, and MCP reference pages.
4. Update release notes or changelog text for any capability version change.
5. Confirm the GitHub Project and Conductor mirrors reflect the contract change.

## Reference Docs

- CLI reference: `docs-site/src/content/docs/api/cli.md`
- OpenAPI reference: `docs-site/src/content/docs/api/openapi.md`
- SDK reference: `docs-site/src/content/docs/api/python.md`
- Client SDK guide: `docs-site/src/content/docs/guides/client-sdk.md`
- MCP adapter surface: `src/nlp_policy_nz/mcp/server.py`
- MCP contract boundary: `conductor/tracks/archive/track84_mcp_server_surface_20260706/spec.md`
