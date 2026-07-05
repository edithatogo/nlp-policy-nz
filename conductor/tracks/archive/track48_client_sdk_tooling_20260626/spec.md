# Track 48: API Client SDK & Developer Tooling

**Dependencies**: Tracks 7, 38, 46
**Parallelization Node**: Developer Experience
**Status**: Planned

## Goal

Provide a first-class developer experience for consuming the nlp-policy-nz API: Python SDK with type hints, CLI shell completion, Docker Compose local development stack, and a step-by-step quickstart guide.

## Scope

### 1. Python Client SDK
- `src/nlp_policy_nz/client/` package wrapping all `/v1/*` endpoints
- Typed request/response models (Pydantic)
- Connection pooling, retry with back-off, timeout configuration
- Async and sync client variants
- Authentication header support (API key)
- SDK published as same PyPI package (or optional `[client]` extra)

### 2. CLI Shell Completion
- Install completion scripts for bash, zsh, and PowerShell
- `nlp-policy-nz completion install` subcommand
- Man-page generation from argparse or click

### 3. Docker Compose Local Dev Stack
- `docker-compose.yml` with API server + LanceDB + optional model cache volume
- Docker Compose override for local development with hot-reload
- Ready-to-use `.env.example` for local config

### 4. Developer Quickstart
- `QUICKSTART.md` with 5-minute setup: Docker Compose up, run a search, view results
- Postman/Insomnia collection for API exploration
- Example scripts in `examples/` directory

## Acceptance Criteria

- [ ] Python client SDK installed via `pip install nlp-policy-nz[client]` or bundled
- [ ] All `/v1/*` endpoints callable from the SDK with type-safe models
- [ ] CLI `completion install` generates working bash/zsh/pwsh completions
- [ ] `docker compose up` launches full stack with API + LanceDB in < 30 seconds
- [ ] `QUICKSTART.md` takes a new user from zero to a successful search in 5 minutes
- [ ] Example scripts run without modification (after `docker compose up`)
