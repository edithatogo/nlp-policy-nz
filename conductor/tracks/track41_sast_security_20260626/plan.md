# Track 41: SAST, Secrets Detection & Security Hardening

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add Bandit to pixi dev dependencies and create `.bandit` config | [x] | conductor_orchestrator |
| 2 | Add Semgrep to pixi dev dependencies with `p/python` rules | [x] | conductor_orchestrator |
| 3 | Add Bandit + Semgrep scan step to CI workflow | [x] | conductor_orchestrator |
| 4 | Add `detect-secrets` pre-commit hook and run baseline scan | [x] | conductor_orchestrator |
| 5 | Create `.secrets.baseline` with reviewed false positives | [x] | conductor_orchestrator |
| 6 | Fix or suppress all initial Bandit/Semgrep findings | [x] | conductor_orchestrator |
| 7 | Create `.github/SECURITY.md` with disclosure policy | [x] | conductor_orchestrator |
| 8 | Verify CI blocks PR with intentional security finding | [x] | conductor_orchestrator |

## 20 November 2026 security migration amendment

The original eight entries above record the historical Semgrep implementation
and remain intact as past evidence. The current replacement uses the
SHA-256-pinned OpenGrep v1.33.1 standalone CLI, a separate PR/default-branch
workflow with synthetic positive/negative controls, and a fail-closed
`--strict --error` scan. The existing `p/python` selection and Bandit,
secret-scanning and dependency gates are preserved.

- [x] Replace the actively executed Semgrep invocation in CI/Makefile
- [x] Add immutable OpenGrep binary provenance and synthetic scanner controls
- [x] Update active security acceptance tests and remove Python dev Semgrep extra
- [ ] Demonstrate rule-ID and finding parity with the previous scanner
- [ ] Refresh and remove the unused `pixi.toml` optional security feature
  and its `pixi.lock` graph using a qualified Pixi resolver
- [ ] Capture exact-head final CI and required-check protection evidence

Do not interpret the historical `complete` track status as completion of
these new migration acceptance criteria.
