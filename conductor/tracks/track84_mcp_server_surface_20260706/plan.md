# Track 84: MCP Server Surface for Agentic Consumption

**Status**: planned
**Dependencies**: Tracks 43, 46, 48, 49, 51, 52, 81
**Parallelization Node**: MCP Agent Surface

## Phase 1: MCP Design and Dependency Gate

- [ ] Task: Add failing tests or fixtures for MCP tool/resource schema generation from Track 81 capability metadata.
- [ ] Task: Evaluate available Python MCP server package options and record the dependency decision.
- [ ] Task: Define read-only initial MCP tools, resources, disabled mutating capabilities, and auth/audit boundaries.
- [ ] Task: Document why MCP remains an adapter over core/API behavior rather than a business-logic layer.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: MCP Design and Dependency Gate' (Protocol in workflow.md).

## Phase 2: MCP Adapter Implementation

- [ ] Task: Add optional MCP dependency wiring and server entrypoint.
- [ ] Task: Implement read-only tools for search, provenance, quality reports, ontology summaries, rules-as-code candidate inspection, and parity reports.
- [ ] Task: Add tests for tool schemas, representative calls, error handling, and disabled write/publish operations.
- [ ] Task: Add local client configuration docs and examples.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: MCP Adapter Implementation' (Protocol in workflow.md).

## Phase 3: Closeout and Mirror

- [ ] Task: Run focused MCP tests, optional dependency checks, docs checks, and relevant lint checks.
- [ ] Task: Verify MCP server startup in stdio mode with fixture-safe commands.
- [ ] Task: Verify GitHub issue and project fields for Track 84.
- [ ] Task: Record follow-on criteria for any future mutating or hosted MCP capabilities.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md).
