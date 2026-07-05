# Track 40: Dependency Automation & Supply Chain Security

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)

## Implementation

- `.github/dependabot.yml`
- `scripts/check_dependency_security.py`
- `src/nlp_policy_nz/security/dependency_security.py`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `pyproject.toml`
- `pixi.toml`
- `Makefile`
- `CONTRIBUTING.md`

## Boundary

Track 40 covers repo-side dependency automation, vulnerability auditing, and
SBOM generation. It does not replace GitHub repository security settings or
Dependabot support gaps for unsupported manifest ecosystems.
