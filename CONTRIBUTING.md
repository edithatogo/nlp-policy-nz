# Contributing to `nlp-policy-nz`

This repository uses Pixi for reproducible development and a conventional
commit style for history hygiene.

## Setup

1. Install the project environment:
   ```bash
   pixi install
   ```
   This installs the Python 3.12 production environment. Use
   `pixi install -e py313-experimental` or
   `pixi install -e py314-experimental` only for runtime compatibility probes.
   CPU, GPU, and profiling environments are documented in
   `docs/python-runtime-matrix.md`.
2. Install pre-commit hooks:
   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```
3. Run the standard validation set before opening a pull request:
   ```bash
   pixi run check
   ```

## Coding Standards

- Keep changes small and reviewable.
- Add or update tests for behavior changes.
- Follow the existing Ruff, type-checking, and docs conventions in the repo.
- Preserve deterministic behavior where the codebase already depends on it.

## Commit Messages

Use conventional commits:

```text
type(scope): short description
```

Examples:

- `feat(governance): add contribution guide`
- `fix(ci): tighten commit message linting`
- `docs(track39): describe repository governance`

## Pull Request Workflow

1. Open a branch with a focused change.
2. Run the relevant tests locally.
3. Fill out the pull request template.
4. Ensure the commit message and PR checklist are clean.
5. Request review from the code owners listed in `.github/CODEOWNERS`.

## Review Expectations

- Highlight user-facing impact.
- Call out any external-service or workflow dependency.
- Describe any limitations that remain after the change.

## Governance

- Security issues should be reported privately through [`.github/SECURITY.md`](./.github/SECURITY.md).
- Inactive issues and pull requests may be labeled stale and later closed by the
  maintenance workflow if they remain inactive.

## Security Checks

- Use `make security-sast` to run Bandit and Semgrep locally.
- Use `make security-secrets` or `pre-commit run detect-secrets --all-files`
  to check staged changes against the secrets baseline.
- Use `make security-deps` to run the dependency vulnerability gate locally.

## Dependency Updates

- Dependabot groups pip version updates into production and development PRs, and
  groups GitHub Actions updates separately.
- Use `make security-deps` to run the dependency vulnerability gate locally.
- Release workflows publish a CycloneDX SBOM alongside the release assets.
- Pixi lockfile refreshes are reviewed together with the PEP 621 manifest
  updates, because Dependabot does not natively update Pixi manifests.
