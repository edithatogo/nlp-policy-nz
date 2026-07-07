# Track 85: Cross-Surface Contract Governance and Release Automation

## Overview

Add the governance and automation needed to keep the CLI, HTTP API, SDK, and MCP surfaces aligned after they are formalized. This track turns interface consistency into a CI-enforced maintenance property.

## Functional Requirements

- Generate a cross-surface conformance matrix from the Track 81 capability registry.
- Add CI checks that fail when CLI, API, SDK, or MCP surfaces drift from the registered capabilities.
- Generate or validate docs for CLI reference, OpenAPI reference, SDK examples, MCP tool/resource reference, and compatibility policy.
- Add release checklist items for contract version changes, deprecations, generated artifacts, and project mirror updates.
- Add examples that exercise the same capability through CLI, API/SDK, and MCP where feasible.
- Record explicit governance for adding, deprecating, or removing public capabilities.

## Non-Functional Requirements

- CI checks must be deterministic and not require external credentials.
- Contract drift reports must be readable enough to act on in pull requests.
- Release automation must preserve existing Conductor and GitHub Project workflows.
- Docs generation should reuse existing scripts where possible.

## Acceptance Criteria

- [x] Cross-surface conformance matrix exists and is generated from the capability registry.
- [x] CI detects registry, CLI, API, SDK, MCP, and docs drift.
- [x] Public docs include CLI, API, SDK, MCP, deprecation, and compatibility references.
- [x] Release checklist covers interface contract versioning and project mirror updates.
- [x] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Implementing new domain capabilities.
- Changing hosting infrastructure.
- Full generated client SDKs for non-Python languages.
