# Track 41: SAST, Secrets Detection & Security Hardening

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Add static application security testing (SAST) and secrets detection to CI to catch security issues before they reach production.

## Scope

- Bandit SAST scanning for Python security issues (SQL injection, command injection, hardcoded passwords, unsafe eval/exec, request-forgery, etc.)
- Semgrep with community rules for additional coverage
- `detect-secrets` or `talisman` pre-commit hook for secrets detection
- `.secrets.baseline` for managing known false positives
- CI gate that blocks PRs on new high-confidence security findings
- Pixi environment hardening: no world-writable files, restricted PATH

## Acceptance Criteria

- [ ] Bandit runs in CI on all source files with severity=high, confidence=high
- [ ] Semgrep runs with at least the `p/python` community rule pack
- [ ] `detect-secrets` pre-commit hook scans staged changes
- [ ] Secrets baseline committed with no actual secrets exposed
- [ ] CI blocks PRs with new Bandit HIGH/HIGH or Semgrep WARNING findings
- [ ] Pre-commit blocks commits with detected secrets
- [ ] Security findings documented and triaged in `.github/SECURITY.md`
