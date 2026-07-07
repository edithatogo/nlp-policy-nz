# Track 81: Interface Surface Contract and Capability Registry

**Status**: planned
**Dependencies**: Tracks 7, 46, 48, 49, 51, 52, 80
**Parallelization Node**: Interface Contract Foundation

## Phase 1: Inventory and Classification

- [x] Task: Add failing tests or validation fixtures for a capability registry with stable IDs and required fields. `tests/test_interface_contract.py`
- [x] Task: Inventory current CLI commands, FastAPI endpoints, SDK methods, and report/export entrypoints. `src/nlp_policy_nz/cli/main.py`, `src/nlp_policy_nz/api/server.py`, `src/nlp_policy_nz/client/*.py`, `src/nlp_policy_nz/interface_contract.py`
- [x] Task: Classify each capability by side effect, auth scope, network dependency, legal-review boundary, and GitHub Actions compatibility. `src/nlp_policy_nz/interface_contract.py`
- [x] Task: Capture adapter gaps where logic lives in CLI/API code instead of reusable core modules. `src/nlp_policy_nz/governance/interface_contract.py`, `docs/interface-contract-governance.md`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Inventory and Classification' (Protocol in workflow.md). `evidence.md`

## Phase 2: Contract Artifact

- [x] Task: Implement the machine-readable capability contract artifact and loader. `src/nlp_policy_nz/interface_contract.py`
- [x] Task: Add schema validation for required fields, stable IDs, duplicate detection, and owner-module references. `tests/test_interface_contract.py`
- [x] Task: Add a decision record documenting the core-library-first adapter model. `docs/interface-contract-governance.md`, `docs/capabilities.md`
- [x] Task: Add documentation explaining how CLI, HTTP API, SDK, and MCP adapters consume the contract. `docs/cli-contract.md`, `docs/interface-contract-governance.md`, `docs/capabilities.md`
- [x] Task: Conductor - User Manual Verification 'Phase 2: Contract Artifact' (Protocol in workflow.md). `evidence.md`

## Phase 3: Closeout and Mirror

- [x] Task: Run focused tests and lint for the registry and documentation paths. `pixi run pytest tests/test_interface_contract.py tests/test_surface_contracts.py tests/test_contract_governance.py tests/test_cli.py tests/test_server.py -q`
- [x] Task: Verify the contract can be validated in GitHub Actions without optional heavyweight model dependencies. `pixi run python scripts/check_interface_surface_contract.py --format markdown`
- [x] Task: Verify GitHub issue and project fields for Track 81. `evidence.md`
- [x] Task: Record follow-on work for CLI, API, MCP, and contract governance tracks. `docs/interface-contract-governance.md`
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md). `evidence.md`
