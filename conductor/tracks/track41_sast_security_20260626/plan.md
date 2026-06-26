# Track 41: SAST, Secrets Detection & Security Hardening

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add Bandit to pixi dev dependencies and create `.bandit` config | [ ] | conductor_orchestrator |
| 2 | Add Semgrep to pixi dev dependencies with `p/python` rules | [ ] | conductor_orchestrator |
| 3 | Add Bandit + Semgrep scan step to CI workflow | [ ] | conductor_orchestrator |
| 4 | Add `detect-secrets` pre-commit hook and run baseline scan | [ ] | conductor_orchestrator |
| 5 | Create `.secrets.baseline` with reviewed false positives | [ ] | conductor_orchestrator |
| 6 | Fix or suppress all initial Bandit/Semgrep findings | [ ] | conductor_orchestrator |
| 7 | Create `.github/SECURITY.md` with disclosure policy | [ ] | conductor_orchestrator |
| 8 | Verify CI blocks PR with intentional security finding | [ ] | conductor_orchestrator |
