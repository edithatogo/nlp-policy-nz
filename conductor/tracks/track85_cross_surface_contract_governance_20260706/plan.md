# Track 85: Cross-Surface Contract Governance and Release Automation

**Status**: planned
**Dependencies**: Tracks 39, 45, 49, 81, 82, 83, 84
**Parallelization Node**: Interface Governance and CI

## Phase 1: Conformance Matrix

- [ ] Task: Add failing tests for conformance matrix generation from the Track 81 registry.
- [ ] Task: Generate a cross-surface matrix for CLI commands, API endpoints, SDK methods, MCP tools/resources, docs, and tests.
- [ ] Task: Add drift detection for missing, extra, or stale capability exposure across surfaces.
- [ ] Task: Make drift reports suitable for CI logs and pull request review.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Conformance Matrix' (Protocol in workflow.md).

## Phase 2: Docs and Release Governance

- [ ] Task: Wire generated or validated docs for CLI, API, SDK, MCP, compatibility, and deprecation references.
- [ ] Task: Add release checklist items for contract versioning, generated artifact refresh, changelog notes, and GitHub Project mirror updates.
- [ ] Task: Add examples that exercise representative capabilities through multiple surfaces.
- [ ] Task: Document governance for adding, changing, deprecating, or removing public capabilities.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Docs and Release Governance' (Protocol in workflow.md).

## Phase 3: Closeout and Mirror

- [ ] Task: Run focused conformance, docs generation, CI-script, and lint checks.
- [ ] Task: Verify GitHub Actions can run the drift checks without credentials or optional model downloads.
- [ ] Task: Verify GitHub issue and project fields for Track 85.
- [ ] Task: Record residual non-Python SDK or hosted-service opportunities as future roadmap notes rather than active scope.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Closeout and Mirror' (Protocol in workflow.md).
