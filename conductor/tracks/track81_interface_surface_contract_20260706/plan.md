# Track 81: Interface Surface Contract and Capability Registry

**Status**: planned
**Dependencies**: Tracks 7, 46, 48, 49, 51, 52, 80
**Parallelization Node**: Interface Contract Foundation

## Phase 1: Inventory and Classification

- [ ] Task: Add failing tests or validation fixtures for a capability registry with stable IDs and required fields.
- [ ] Task: Inventory current CLI commands, FastAPI endpoints, SDK methods, and report/export entrypoints.
- [ ] Task: Classify each capability by side effect, auth scope, network dependency, legal-review boundary, and GitHub Actions compatibility.
- [ ] Task: Capture adapter gaps where logic lives in CLI/API code instead of reusable core modules.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Inventory and Classification' (Protocol in workflow.md).

## Phase 2: Contract Artifact

- [ ] Task: Implement the machine-readable capability contract artifact and loader.
- [ ] Task: Add schema validation for required fields, stable IDs, duplicate detection, and owner-module references.
- [ ] Task: Add a decision record documenting the core-library-first adapter model.
- [ ] Task: Add documentation explaining how CLI, HTTP API, SDK, and MCP adapters consume the contract.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Contract Artifact' (Protocol in workflow.md).

## Phase 3: Closeout and Mirror

- [ ] Task: Run focused tests and lint for the registry and documentation paths.
- [ ] Task: Verify the contract can be validated in GitHub Actions without optional heavyweight model dependencies.
- [ ] Task: Verify GitHub issue and project fields for Track 81.
- [ ] Task: Record follow-on work for CLI, API, MCP, and contract governance tracks.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md).
