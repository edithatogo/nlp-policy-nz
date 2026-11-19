# Track 41: SAST, Secrets Detection & Security Hardening

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Add static application security testing (SAST) and secrets detection to CI to catch security issues before they reach production.

## Scope

- Bandit SAST scanning for Python security issues (SQL injection, command injection, hardcoded passwords, unsafe eval/exec, request-forgery, etc.)
- OpenGrep with community rules for additional coverage, replacing Semgrep with pinned binary and fail-closed analysis
- `detect-secrets` or `talisman` pre-commit hook for secrets detection
- `.secrets.baseline` for managing known false positives
- CI gate that blocks PRs on new high-confidence security findings
- Pixi environment hardening: no world-writable files, restricted PATH

## Acceptance Criteria

- [ ] Bandit runs in CI on all source files with severity=high, confidence=high
- [ ] OpenGrep runs with `p/python` on PRs and default-branch pushes, with pinned scanner, source inventory and synthetic controls
- [ ] `detect-secrets` pre-commit hook scans staged changes
- [ ] Secrets baseline committed with no actual secrets exposed
- [ ] CI blocks PRs on OpenGrep WARNING findings and scanner/parser errors; preserve existing Bandit HIGH/HIGH default-branch gate
- [ ] Pre-commit blocks commits with detected secrets
- [ ] Security findings documented and triaged in `.github/SECURITY.md`
