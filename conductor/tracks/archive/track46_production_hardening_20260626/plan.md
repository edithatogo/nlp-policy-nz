# Track 46: Production Hardening & API Maturity [fe5c561]

**Dependencies**: Tracks 7, 23, 38, 44
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Refactor FastAPI routes to versioned prefix (`/v1/` and `/v2/`); move hardcoded version string to `VERSION.json` (from Track 45); add CORS middleware allowing configurable origins | [x] | conductor_orchestrator |
| 2 | Create environment config files (`.env.dev`, `.env.staging`, `.env.prod`); update all integrations to read env-var-based endpoints and secrets | [x] | conductor_orchestrator |
| 3 | Create `.github/workflows/deploy-staging.yml` that deploys to staging on PR merge, runs smoke tests, then gates prod deploy | [x] | conductor_orchestrator |
| 4 | Add `schema_version` field to PipelineRecord; create `data/migrations/` directory with migration registry and first migration script | [x] | conductor_orchestrator |
| 5 | Add backward compatibility test suite: run old PipelineRecord schema through current pipeline, assert no data loss | [x] | conductor_orchestrator |
| 6 | Create Locust test scenarios in `tests/load/` for API endpoints (`/v1/embed`, `/v1/search`, `/v1/process`); add CI workflow `load-test.yml` | [x] | conductor_orchestrator |
| 7 | Implement feature flag system in `src/nlp_policy_nz/config/feature_flags.py`; wire into pipeline stage gating and endpoint enable/disable | [x] | conductor_orchestrator |
| 8 | Upgrade `/health` endpoint to check DB connection, model loaded, pipeline status, last-run timestamp; add graceful shutdown bookkeeping; add token-bucket rate limiting middleware | [x] | conductor_orchestrator |
| 9 | Fix async safety: move sync embedding/search/file-process calls to worker threads to avoid blocking the event loop | [x] | conductor_orchestrator |
| 10 | Make uvicorn worker count configurable via `UVICORN_WORKERS` env var (default 1 for dev, 4+ for prod) | [x] | conductor_orchestrator |
| 11 | Document runbook in `docs/ops/runbook.md` covering: API down, DB corruption, model load failure, pipeline hang, HF/Zenodo API auth failure, rate limit exceeded | [x] | conductor_orchestrator |
| 12 | Write tests for health check, rate limiting, feature flags, migration forward/backward, backward compat, async safety, CORS | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side API routes, configs, migration scripts, test suites, and runbook satisfy planning and implementation evidence. Live load test results, staging deployment, and production rollout require infrastructure access.
