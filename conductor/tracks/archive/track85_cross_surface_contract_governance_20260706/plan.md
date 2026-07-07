# Track 85: Cross-Surface Contract Governance and Release Automation

**Status**: archived
**Dependencies**: Tracks 39, 45, 49, 81, 82, 83, 84
**Parallelization Node**: Interface Governance and CI

## Phase 1: Conformance Matrix

- [x] Task: Add failing tests for conformance matrix generation from the Track 81 registry. `tests/test_track85_interface_surface_contract.py`, `tests/test_contract_governance.py`
- [x] Task: Generate a cross-surface matrix for CLI commands, API endpoints, SDK methods, MCP tools/resources, docs, and tests. `src/nlp_policy_nz/contract_governance.py`, `src/nlp_policy_nz/governance/interface_contract.py`
- [x] Task: Add drift detection for missing, extra, or stale capability exposure across surfaces. `src/nlp_policy_nz/governance/interface_contract.py`, `scripts/check_interface_surface_contract.py`
- [x] Task: Make drift reports suitable for CI logs and pull request review. `src/nlp_policy_nz/governance/interface_contract.py`, `tests/test_track85_interface_surface_contract.py`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Conformance Matrix' (Protocol in workflow.md). `evidence.md`

## Phase 2: Docs and Release Governance

- [x] Task: Wire generated or validated docs for CLI, API, SDK, MCP, compatibility, and deprecation references. `docs/interface-contract-governance.md`, `docs/cli-contract.md`, `docs-site/src/content/docs/api/openapi.md`, `docs-site/src/content/docs/api/python.md`
- [x] Task: Add release checklist items for contract versioning, generated artifact refresh, changelog notes, and GitHub Project mirror updates. `src/nlp_policy_nz/contract_governance.py`, `docs/interface-contract-governance.md`
- [x] Task: Add examples that exercise representative capabilities through multiple surfaces. `tests/test_track83_api_contract.py`, `tests/test_mcp_server.py`, `tests/test_surface_contracts.py`
- [x] Task: Document governance for adding, changing, deprecating, or removing public capabilities. `docs/interface-contract-governance.md`, `conductor/tracks/track85_cross_surface_contract_governance_20260706/spec.md`
- [x] Task: Conductor - User Manual Verification 'Phase 2: Docs and Release Governance' (Protocol in workflow.md). `evidence.md`

## Phase 3: Closeout and Mirror

- [x] Task: Run focused conformance, docs generation, CI-script, and lint checks. `tests/test_track85_interface_surface_contract.py`, `src/nlp_policy_nz/governance/interface_contract.py`, `docs/interface-contract-governance.md`
- [x] Task: Verify GitHub Actions can run the drift checks without credentials or optional model downloads. `scripts/check_interface_surface_contract.py`, `tests/test_track85_interface_surface_contract.py`
- [x] Task: Verify GitHub issue and project fields for Track 85. `evidence.md`
- [x] Task: Record residual non-Python SDK or hosted-service opportunities as future roadmap notes rather than active scope. `evidence.md`
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md). `evidence.md`
