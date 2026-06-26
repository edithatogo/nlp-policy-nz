# Track 40: Dependency Automation & Supply Chain Security

**Dependencies**: Track 1
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Automate dependency updates, add vulnerability scanning to CI, and generate software bills of materials (SBOM) for supply-chain transparency and governance compliance.

## Scope

- Dependabot configuration for pip (pyproject.toml), pixi (pixi.toml), GitHub Actions
- Weekly grouped dependency PRs (dev, runtime, actions)
- `pip-audit` or `safety` scanning in CI on every PR
- CycloneDX SBOM generation via `cyclonedx-bom` or `pip-audit --sbom`
- SBOM artifact upload to CI for auditing
- Policy: fail CI on critical/high severity known vulnerabilities

## Acceptance Criteria

- [ ] `.github/dependabot.yml` configured for pip, pixi, and GitHub Actions
- [ ] Dependabot creates grouped dependency PRs (not one-per-dep)
- [ ] CI pipeline runs `pip-audit` (or safety) on changed dependencies
- [ ] CI fails on critical (CVSS >= 9.0) vulnerabilities
- [ ] CI generates CycloneDX JSON SBOM as build artifact
- [ ] SBOM is attached to GitHub releases
- [ ] Document dependency update policy in CONTRIBUTING.md
