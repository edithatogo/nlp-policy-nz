# Track 84: MCP Server Surface for Agentic Consumption

**Status**: archived
**Dependencies**: Tracks 43, 46, 48, 49, 51, 52, 81
**Parallelization Node**: MCP Agent Surface

## Phase 1: MCP Design and Dependency Gate

- [x] Task: Add failing tests or fixtures for MCP tool/resource schema generation from Track 81 capability metadata. `tests/test_mcp_server.py`, `tests/test_surface_contracts.py`
- [x] Task: Evaluate available Python MCP server package options and record the dependency decision. `src/nlp_policy_nz/mcp/server.py`, `docs/interface-contract-governance.md`
- [x] Task: Define read-only initial MCP tools, resources, disabled mutating capabilities, and auth/audit boundaries. `src/nlp_policy_nz/mcp/server.py`, `docs/interface-contract-governance.md`
- [x] Task: Document why MCP remains an adapter over core/API behavior rather than a business-logic layer. `docs/interface-contract-governance.md`, `conductor/tracks/archive/track84_mcp_server_surface_20260706/spec.md`
- [x] Task: Conductor - User Manual Verification 'Phase 1: MCP Design and Dependency Gate' (Protocol in workflow.md). `evidence.md`

## Phase 2: MCP Adapter Implementation

- [x] Task: Add optional MCP dependency wiring and server entrypoint. `src/nlp_policy_nz/mcp/server.py`, `src/nlp_policy_nz/mcp/__init__.py`
- [x] Task: Implement read-only tools for search, provenance, quality reports, ontology summaries, rules-as-code candidate inspection, and parity reports. `src/nlp_policy_nz/mcp/server.py`, `tests/test_mcp_server.py`
- [x] Task: Add tests for tool schemas, representative calls, error handling, and disabled write/publish operations. `tests/test_mcp_server.py`, `tests/test_surface_contracts.py`
- [x] Task: Add local client configuration docs and examples. `docs/interface-contract-governance.md`, `docs/capabilities.md`
- [x] Task: Conductor - User Manual Verification 'Phase 2: MCP Adapter Implementation' (Protocol in workflow.md). `evidence.md`

## Phase 3: Closeout and Mirror

- [x] Task: Run focused MCP tests, optional dependency checks, docs checks, and relevant lint checks. `tests/test_mcp_server.py`, `tests/test_surface_contracts.py`, `docs/interface-contract-governance.md`
- [x] Task: Verify MCP server startup in stdio mode with fixture-safe commands. `src/nlp_policy_nz/mcp/server.py`, `tests/test_mcp_server.py`
- [x] Task: Verify GitHub issue and project fields for Track 84. `evidence.md`
- [x] Task: Record follow-on criteria for any future mutating or hosted MCP capabilities. `evidence.md`
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md). `evidence.md`
