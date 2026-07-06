# Track 84: MCP Server Surface for Agentic Consumption

## Overview

Add an optional Model Context Protocol server surface on top of the existing core library and Track 81 capability contract. The MCP server should make `nlp-policy-nz` usable by local agents without making MCP the business-logic layer.

## Functional Requirements

- Evaluate the current Python MCP server package options during implementation and choose the smallest stable dependency that works in GitHub Actions.
- Add an optional MCP extra or isolated dependency path so the core package does not require MCP dependencies by default.
- Expose read-only tools first for search, provenance inspection, quality reports, ontology/knowledge graph summaries, rules-as-code candidate inspection, and multi-engine parity reports.
- Expose resources for schemas, capability metadata, generated docs, and selected Conductor status artifacts where safe.
- Map every MCP tool/resource back to Track 81 capability IDs and side-effect classifications.
- Add local configuration docs for Codex, Claude Desktop, and generic stdio MCP clients where applicable.

## Non-Functional Requirements

- MCP tools must be deterministic, local-first, and credential-safe by default.
- Mutating, publishing, or external-network tools must remain disabled until explicitly designed with auth and audit gates.
- MCP tests must run in GitHub Actions without requiring a desktop client.
- The MCP adapter must call core modules or API clients, not duplicate pipeline logic.

## Acceptance Criteria

- [ ] Optional MCP server module and entrypoint exist without adding a mandatory runtime dependency.
- [ ] Read-only MCP tools and resources are mapped to Track 81 capability IDs.
- [ ] Contract tests exercise MCP tool schemas and representative tool calls with fixture data.
- [ ] Docs cover local MCP client configuration, safety boundaries, and disabled write/publish capabilities.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Remote multi-user MCP hosting.
- Autonomous write/publish tools.
- Replacing the HTTP API or CLI.
