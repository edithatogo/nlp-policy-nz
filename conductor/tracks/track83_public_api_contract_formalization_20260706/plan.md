# Track 83: Public API Contract Formalization

**Status**: planned
**Dependencies**: Tracks 46, 48, 51, 52, 81
**Parallelization Node**: HTTP API Product Surface

## Phase 1: API Contract Baseline

- [ ] Task: Add failing tests for deterministic OpenAPI generation and public endpoint inventory.
- [ ] Task: Map API endpoints and SDK methods to Track 81 capability IDs.
- [ ] Task: Capture current request/response models, auth scopes, and error contracts.
- [ ] Task: Identify endpoint or SDK drift against the capability registry.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: API Contract Baseline' (Protocol in workflow.md).

## Phase 2: API and SDK Formalization

- [ ] Task: Generate and pin versioned OpenAPI artifacts.
- [ ] Task: Add contract tests for validation errors, RFC 7807 payloads, auth/scope behavior, and health/version endpoints.
- [ ] Task: Align sync and async SDK methods with the supported API capability set.
- [ ] Task: Add API lifecycle, versioning, deprecation, and local startup docs.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: API and SDK Formalization' (Protocol in workflow.md).

## Phase 3: Closeout and Mirror

- [ ] Task: Run focused API, SDK, OpenAPI, and lint checks.
- [ ] Task: Verify generated API docs and OpenAPI artifacts do not drift.
- [ ] Task: Verify GitHub issue and project fields for Track 83.
- [ ] Task: Record remaining intentional API gaps and promotion criteria.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md).
