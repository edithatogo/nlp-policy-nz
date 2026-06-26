# Track 46: Production Hardening & API Maturity

**Dependencies**: Tracks 7, 23, 38, 44
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Refactor FastAPI routes to versioned prefix (`/v1/`), add deprecation header support and API version manifest | [ ] | conductor_orchestrator |
| 2 | Create environment config files (`.env.dev`, `.env.staging`, `.env.prod`); update all integrations to read env-var-based endpoints | [ ] | conductor_orchestrator |
| 3 | Create `.github/workflows/deploy-staging.yml` that deploys to staging on PR merge, runs smoke tests, then gates prod deploy | [ ] | conductor_orchestrator |
| 4 | Add `schema_version` field to PipelineRecord; create `data/migrations/` directory with migration registry and first migration script | [ ] | conductor_orchestrator |
| 5 | Add backward compatibility test suite: run old PipelineRecord schema through current pipeline, assert no data loss | [ ] | conductor_orchestrator |
| 6 | Create Locust test scenarios in `tests/load/` for API endpoints; add CI workflow `load-test.yml` | [ ] | conductor_orchestrator |
| 7 | Implement feature flag system in `src/nlp_policy_nz/config/feature_flags.py`; wire into pipeline stage gating | [ ] | conductor_orchestrator |
| 8 | Add `/health` endpoint, graceful shutdown handler, rate limiting middleware to FastAPI server | [ ] | conductor_orchestrator |
| 9 | Document runbook in `docs/ops/runbook.md` covering: API down, DB corruption, model load failure, pipeline hang, HF/Zenodo API auth failure | [ ] | conductor_orchestrator |
| 10 | Write tests for health check, rate limiting, feature flags, migration forward/backward, and backward compat | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side API routes, configs, migration scripts, test suites, and runbook satisfy planning and implementation evidence. Live load test results, staging deployment, and production rollout require infrastructure access.
