# Track 52: Observability & Error Standardization

**Dependencies**: Tracks 19, 46, 51
**Parallelization Node**: Security & Observability
**Status**: Planned

## Goal

Make the API fully observable in production: structured JSON logging for machine-parsable operations, standardized error responses (RFC 7807) for consistent client handling, request ID tracing across the request lifecycle, Prometheus metrics for monitoring, and graceful degradation when dependencies fail.

## Scope

### 1. Structured JSON Logging
- Replace `logging` string formatting with structlog or python-json-logger
- Every log entry: timestamp, level, logger, message, request_id, endpoint, duration_ms
- Request-scoped context: request_id injected via FastAPI middleware and propagated through pipeline calls
- Application startup/shutdown logged with version and config hash
- Log level configurable via `LOG_LEVEL` env var

### 2. RFC 7807 Standardized Error Responses
- All HTTP errors return `application/problem+json` with: `type`, `title`, `status`, `detail`, `instance`
- Error code taxonomy: `AUTH_INVALID_KEY`, `AUTH_INSUFFICIENT_SCOPE`, `MODEL_NOT_LOADED`, `PIPELINE_FAILURE`, `VALIDATION_ERROR`, `RATE_LIMITED`, `NOT_FOUND`
- Validation errors include `errors` array with field-level details
- OpenAPI schema updated to include problem detail response models
- Client SDK (Track 48) updated to parse structured errors

### 3. Request ID Tracing
- UUID request_id generated per request in middleware
- Request_id propagated to all downstream calls via contextvars
- Request_id included in all logs, error responses, and response headers (`X-Request-ID`)
- Async context propagation for thread-pool tasks (Track 46 async safety)

### 4. Prometheus Metrics
- `/metrics` endpoint exposing Prometheus metrics via prometheus-fastapi-instrumentator
- Request count, duration histogram, error count by status code, endpoint, scope
- Model load state gauge (0/1)
- Active request gauge, queue depth
- Pipeline run duration histogram

### 5. Graceful Degradation
- Track 46 async safety + feature flags enable degraded mode
- If embedding model fails to load: `/embed` returns 503, `/search` falls back to keyword-only, `/process` runs without embeddings
- Startup probe reports model load progress
- Readiness probe reports when pipeline is fully operational
- Liveness probe for basic process health

## Acceptance Criteria

- [ ] All log entries are valid JSON with timestamp, level, request_id, and message
- [ ] All error responses follow RFC 7807 format with error codes from defined taxonomy
- [ ] `X-Request-ID` header returned on every response
- [ ] `/metrics` returns Prometheus-format metrics with request counts and durations
- [ ] When embedding model is unavailable, `/search` returns degraded results (keyword-only) with 200 + `X-Degraded: true` header
- [ ] When embedding model is unavailable, `/embed` returns 503 with problem detail
- [ ] OpenAPI schema includes problem detail response schemas
