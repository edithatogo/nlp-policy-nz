# Track 46: Production Hardening & API Maturity

**Dependencies**: Tracks 7, 23, 38, 44
**Parallelization Node**: Infrastructure & Quality
**Status**: Planned

## Goal

Transition nlp-policy-nz from a research alpha/beta to a mature, hardened, stable end-product with production-grade API versioning, environment separation, data migration, load testing, backward compatibility, and operational readiness.

## Scope

### 1. API Versioning & Lifecycle
- FastAPI prefix routing (`/v1/`, `/v2/`) with deprecation headers
- API version manifest and changelog
- Deprecation policy: announce, sunset-date, removal
- Backward compatibility testing: run v1 tests against v2 API to detect breaks

### 2. Environment Separation
- Dev/staging/prod environment configs (`.env.dev`, `.env.staging`, `.env.prod`)
- Environment-specific secrets and endpoints (HF, Zenodo, OSF sandbox vs prod)
- Staging CI/CD workflow that mirrors production deployment
- Smoke tests that run in each environment on deploy

### 3. Database & Schema Migration Strategy
- PipelineRecord schema version field and migration registry
- Forward-only migration scripts in `data/migrations/`
- Rollback procedure for each migration
- Schema compatibility testing: old code reads new data and vice versa

### 4. Load & Stress Testing
- Locust or k6 test scenarios for the FastAPI server: concurrent users, batch processing, search queries
- Benchmarked throughput baseline: requests/second, latency percentiles (p50/p95/p99)
- Stress test to breaking point; document capacity limits
- CI integration: load test runs weekly, results published to artifact

### 5. Feature Flags & Gradual Rollout
- Feature flag system (env-var or JSON-based) enabling/disabling pipeline stages
- Canary deployment: run new pipeline version on 10% of corpus before full rollout
- Kill switch: disable problematic pipeline stage without redeploy

### 6. Operational Readiness
- Health check endpoint (`/health`): pipeline status, DB connection, model loaded, last run timestamp
- Graceful shutdown: complete in-flight pipeline runs before SIGTERM
- Rate limiting: per-IP and per-token limits on FastAPI
- Backup & restore procedure for LanceDB + metadata stores
- Runbook documenting common failure scenarios and recovery steps

## Acceptance Criteria

- [ ] API serves both `/v1/` and `/v2/` endpoints simultaneously with deprecation headers
- [ ] Dev/staging/prod environments deploy independently with correct configs
- [ ] Staging CI runs full test suite against staging deployment before prod deploy
- [ ] PipelineRecord schema migration runs forward and backward without data loss
- [ ] Load test achieves documented throughput baseline with p99 latency < 2s
- [ ] Feature flags disable pipeline stages without code change
- [ ] `/health` endpoint returns pipeline OK/degraged/down status
- [ ] Rate limiting blocks abusive clients with 429 responses
- [ ] Runbook covers recovery for top 5 failure scenarios
