# Track 39: Repository Governance & Contribution Framework

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)

## Implementation

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/release-drafter.yml`
- `.github/workflows/release-drafter.yml`
- `.github/workflows/stale.yml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `scripts/check_commit_message.py`
- `src/nlp_policy_nz/governance/commit_message.py`

## Boundary

Track 39 covers repository governance, contributor guidance, and automated
maintenance workflows. It does not replace repository settings that must be
configured in GitHub itself, such as branch protection or required review
settings.
