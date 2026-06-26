# Track 52: Observability & Error Standardization

**Dependencies**: Tracks 19, 46, 51
**Parallelization Node**: Security & Observability
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add structlog dependency; replace all `logging.getLogger(...)` calls in `src/nlp_policy_nz/api/server.py` with structlog; configure JSON rendering | [ ] | conductor_orchestrator |
| 2 | Add FastAPI middleware that generates `request_id` (uuid4), injects into `contextvars`, adds `X-Request-ID` response header, and includes in all log entries | [ ] | conductor_orchestrator |
| 3 | Create `src/nlp_policy_nz/api/errors.py` with RFC 7807 `ProblemDetail` model, error code taxonomy enum, and exception handler that converts all HTTPException + validation errors to problem+json | [ ] | conductor_orchestrator |
| 4 | Add prometheus-fastapi-instrumentator; configure `/metrics` endpoint with request count, duration histogram, error count, model state gauge, active request gauge | [ ] | conductor_orchestrator |
| 5 | Implement graceful degradation: catch model load failure, set feature flag `degraded_embeddings`, route `/embed` to 503 and `/search` to keyword-only fallback with `X-Degraded: true` header | [ ] | conductor_orchestrator |
| 6 | Add startup/readiness/liveness probes: startup checks model load, readiness checks pipeline + DB, liveness is basic process | [ ] | conductor_orchestrator |
| 7 | Update OpenAPI schema to include ProblemDetail response models for all endpoints | [ ] | conductor_orchestrator |
| 8 | Update client SDK (Track 48) to parse RFC 7807 errors with proper error type matching | [ ] | conductor_orchestrator |
| 9 | Write tests: structured log entries are valid JSON, error responses are problem+json, degraded mode fallbacks, metrics endpoint returns valid prometheus format | [ ] | conductor_orchestrator |
| 10 | Document observability in `docs/ops/observability.md`: log format, error codes, metrics reference, degraded mode behavior | [ ] | conductor_orchestrator |

## Evidence Boundary

Structured logging config, error handler, metrics instrumentation, degradation logic, probe endpoints, and tests satisfy repo-side evidence. Prometheus/Grafana dashboard setup requires external infrastructure.
