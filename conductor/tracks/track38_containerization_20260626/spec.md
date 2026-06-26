# Track 38: Containerization & Reproducible Execution

**Dependencies**: Track 1, Track 23
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Provide Docker-based container images for development, CI, and production environments, plus a .devcontainer specification for instant onboarding in GitHub Codespaces or VS Code Remote.

## Scope

- Multi-stage Dockerfile: builder stage with pixi, lightweight runtime stage
- `.devcontainer/devcontainer.json` with pixi, pre-commit, and recommended extensions
- `docker-compose.yml` for local service dependencies (LanceDB, Postgres if used)
- CI integration: build and test inside the Docker image as a reproducibility check
- `.dockerignore` for efficient context exclusion

## Acceptance Criteria

- [ ] `Dockerfile` with pixi-based multi-stage build producing a <1GB runtime image
- [ ] `docker build` completes in <5 minutes on CI
- [ ] `docker run` executes the full pipeline test suite with zero failures
- [ ] `.devcontainer/devcontainer.json` loads the image and runs pre-commit on commit
- [ ] `docker-compose.yml` starts all external service dependencies with one command
- [ ] CI workflow (`containerized-ci.yml`) runs tests inside the container to verify reproducibility
