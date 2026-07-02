# Track 48: API Client SDK & Developer Tooling

**Dependencies**: Tracks 7, 38, 46
**Parallelization Node**: Developer Experience
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Create `src/nlp_policy_nz/client/` package with base client, connection pool, retry logic, and typed models for all `/v1/*` endpoints | [x] | conductor_orchestrator |
| 2 | Implement async client variant using `httpx.AsyncClient` for non-blocking calls | [x] | conductor_orchestrator |
| 3 | Add `[client]` extra to `pyproject.toml`; verify `pip install nlp-policy-nz[client]` installs SDK deps only | [x] | conductor_orchestrator |
| 4 | Add `completion install` subcommand to CLI generating bash/zsh/pwsh completions; add man-page generation | [x] | conductor_orchestrator |
| 5 | Create `docker-compose.yml` with `api`, `lancedb`, and `model-cache` services; add `.env.example` | [x] | conductor_orchestrator |
| 6 | Write `QUICKSTART.md` with 5-minute tutorial; create `examples/` directory with 3 example scripts | [x] | conductor_orchestrator |
| 7 | Write tests for client SDK: request building, response parsing, retry behavior, error handling | [x] | conductor_orchestrator |

## Evidence Boundary

Client SDK code, shell completion scripts, Docker Compose YAML, quickstart guide, and example scripts satisfy repo-side evidence. Postman collection export is optional.
