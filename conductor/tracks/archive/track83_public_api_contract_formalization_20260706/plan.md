# Track 83: Public API Contract Formalization

**Status**: archived
**Dependencies**: Tracks 46, 48, 51, 52, 81
**Parallelization Node**: HTTP API Product Surface

## Phase 1: API Contract Baseline

- [x] Task: Add failing tests for deterministic OpenAPI generation and public endpoint inventory. `tests/test_track83_api_contract.py`
- [x] Task: Map API endpoints and SDK methods to Track 81 capability IDs. `src/nlp_policy_nz/api/server.py`, `src/nlp_policy_nz/capabilities.py`
- [x] Task: Capture current request/response models, auth scopes, and error contracts. `src/nlp_policy_nz/api/server.py`, `src/nlp_policy_nz/client/models.py`, `tests/test_track83_api_contract.py`
- [x] Task: Identify endpoint or SDK drift against the capability registry. `tests/test_track83_api_contract.py`, `docs/interface-contract-governance.md`
- [x] Task: Conductor - User Manual Verification 'Phase 1: API Contract Baseline' (Protocol in workflow.md). `evidence.md`

## Phase 2: API and SDK Formalization

- [x] Task: Generate and pin versioned OpenAPI artifacts. `docs-site/src/content/docs/api/openapi.json`, `docs-site/src/content/docs/api/openapi.md`
- [x] Task: Add contract tests for validation errors, RFC 7807 payloads, auth/scope behavior, and health/version endpoints. `tests/test_track83_api_contract.py`, `tests/test_server.py`, `tests/test_track46_production_hardening.py`
- [x] Task: Align sync and async SDK methods with the supported API capability set. `src/nlp_policy_nz/client/sync.py`, `src/nlp_policy_nz/client/async_client.py`, `tests/test_track83_api_contract.py`
- [x] Task: Add API lifecycle, versioning, deprecation, and local startup docs. `docs/interface-contract-governance.md`, `docs/ops/api_security.md`, `docs-site/src/content/docs/api/openapi.md`
- [x] Task: Conductor - User Manual Verification 'Phase 2: API and SDK Formalization' (Protocol in workflow.md). `evidence.md`

## Phase 3: Closeout and Mirror

- [x] Task: Run focused API, SDK, OpenAPI, and lint checks. `tests/test_track83_api_contract.py`, `docs-site/src/content/docs/api/openapi.md`
- [x] Task: Verify generated API docs and OpenAPI artifacts do not drift. `docs-site/src/content/docs/api/openapi.json`, `docs-site/src/content/docs/api/openapi.md`, `docs-site/src/content/docs/api/python.md`
- [x] Task: Verify GitHub issue and project fields for Track 83. `evidence.md`
- [x] Task: Record remaining intentional API gaps and promotion criteria. `evidence.md`
- [x] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md). `evidence.md`
