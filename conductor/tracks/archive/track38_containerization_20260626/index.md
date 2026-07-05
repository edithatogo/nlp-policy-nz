# Track 38: Containerization & Reproducible Execution

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)

## Implementation

- `Dockerfile`
- `.dockerignore`
- `.devcontainer/devcontainer.json`
- `docker-compose.yml`
- `.github/workflows/containerized-ci.yml`
- `.github/workflows/docker-publish.yml`
- `src/nlp_policy_nz/deployment/container_checks.py`
- `tests/test_track38_containerization.py`

## Boundary

Track 38 covers repo-side container definitions and reproducible execution
checks. Local build verification still depends on a Docker runtime being
available on the workstation or CI runner.
