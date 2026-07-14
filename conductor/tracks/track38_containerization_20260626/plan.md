# Track 38: Containerization & Reproducible Execution

**Dependencies**: Track 1, Track 23
**Parallelization Node**: Infrastructure & Quality
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Create `.dockerignore` excluding `.tmp/`, `artifacts/`, `data/`, `__pycache__` | [x] | conductor_orchestrator |
| 2 | Write multi-stage `Dockerfile` with pixi install + runtime layer | [x] | conductor_orchestrator |
| 3 | Verify `docker build` succeeds and `docker run` passes smoke tests | [x] | conductor_orchestrator |
| 4 | Create `.devcontainer/devcontainer.json` with pixi, pre-commit, Python, and Ruff extensions | [x] | conductor_orchestrator |
| 5 | Create `docker-compose.yml` for LanceDB and other service dependencies | [x] | conductor_orchestrator |
| 6 | Add `containerized-ci.yml` workflow that builds image and runs tests inside container | [x] | conductor_orchestrator |
| 7 | Write tests verifying container can reach external services | [x] | conductor_orchestrator |
| 8 | Configure multi-architecture build (linux/amd64, linux/arm64) with GitHub Actions matrix; push to GHCR on version tags | [x] | conductor_orchestrator |
| 9 | Add HEALTHCHECK instruction to Dockerfile; add Dockerfile linter (hadolint) to CI | [x] | conductor_orchestrator |
| 10 | Run container as non-root user with `--user` mapping; verify file permissions for output directories | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side Docker/devcontainer files, working multi-arch builds, and GHCR publication satisfy this track.

## Verification Note

Local Docker verification was attempted on 2026-07-02, but the Windows workstation does not have the Docker CLI available. GitHub Actions verified the pushed container workflow on 2026-07-02: Containerized CI run https://github.com/edithatogo/nlp-policy-nz/actions/runs/28560448862 passed `docker build`, Track 38 container contract tests, repo smoke tests inside the container, and non-root output permission checks.
