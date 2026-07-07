# Track 81: Interface Surface Contract and Capability Registry

## Overview

Formalize the existing CLI, FastAPI, client SDK, and future MCP surfaces around a shared capability contract. The goal is to make the core library the authoritative implementation layer, with each external surface acting as a thin, tested adapter.

## Functional Requirements

- Inventory current CLI commands, FastAPI endpoints, SDK methods, and rules-as-code/reporting capabilities.
- Define stable capability IDs, descriptions, inputs, outputs, auth scopes, side-effect levels, error shapes, and versioning metadata.
- Classify capabilities as read-only, write, publishing, destructive, external-network, or local-only.
- Map each capability to existing core functions and identify gaps where logic is still embedded directly in a surface adapter.
- Produce a machine-readable registry that can drive CLI/API/MCP docs, contract tests, and future generated adapters.
- Record a migration decision for keeping business logic in core modules instead of the CLI, FastAPI, or MCP server.

## Non-Functional Requirements

- The registry must be deterministic and safe to validate in GitHub Actions.
- No production behavior changes are required until downstream tracks implement adapter alignment.
- Capability metadata must be explicit about legal-review, provenance, and fail-closed boundaries for rules-as-code workflows.
- The contract must support future deprecation and versioning without breaking existing CLI or API consumers.

## Acceptance Criteria

- [x] Capability inventory covers CLI, FastAPI, SDK, rules-as-code exports, quality reports, search, provenance, and multi-engine parity.
- [x] A machine-readable interface contract exists with stable IDs, schemas, auth/scope metadata, side-effect classification, and owner modules.
- [x] Adapter gap report identifies duplicated logic and missing core functions.
- [x] Decision record confirms the core-library-first adapter model for CLI, API, and MCP surfaces.
- [x] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Rewriting every adapter.
- Implementing the MCP server.
- Changing auth policy beyond recording required scopes.
