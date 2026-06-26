# Track 39: Repository Governance & Contribution Framework

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Create a complete repository governance and contribution framework to enable external contributors, standardise issue/PR workflows, and automate repository maintenance.

## Scope

- `CONTRIBUTING.md` with development setup, coding standards, PR workflow, and review guidelines
- `.github/CODEOWNERS` for automatic review assignment by area
- `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- Commit message linting via pre-commit or CI (conventional commits)
- Stale issue/PR management via `actions/stale`
- GitHub label standardization (`kind/*`, `area/*`, `priority/*`, `track/*`)
- `.github/release-drafter.yml` for automated changelog generation

## Acceptance Criteria

- [ ] `CONTRIBUTING.md` covers setup, conventions, and PR lifecycle
- [ ] Issue templates render correctly in GitHub UI with structured fields
- [ ] PR template includes checklist for quality gates, tests, and changelog
- [ ] `CODEOWNERS` assigns reviews by package area (semantic/, syntactic/, discourse/, training/, etc.)
- [ ] Commit messages are linted on PR via CI (or pre-commit)
- [ ] Stale bot marks issues/PRs inactive >90d and closes after 14d reminder
- [ ] Release drafter auto-generates changelog from conventional commits
