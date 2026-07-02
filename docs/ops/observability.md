# Observability

## Logging

- Log format: JSON lines to stderr
- Fields: timestamp, level, logger, message, request_id, endpoint, method, status, duration_ms, degraded
- Request IDs are generated per request and returned in `X-Request-ID`
- Startup and shutdown events log the active version and a configuration hash

## Errors

All API errors are rendered as `application/problem+json` with these standardized codes:

- `AUTH_INVALID_KEY`
- `AUTH_INSUFFICIENT_SCOPE`
- `MODEL_NOT_LOADED`
- `PIPELINE_FAILURE`
- `VALIDATION_ERROR`
- `RATE_LIMITED`
- `NOT_FOUND`

Validation errors include field-level details in an `errors` array.

## Metrics

The API exposes Prometheus-format metrics at `/metrics`.

Key series:

- `nlp_policy_nz_requests_total`
- `nlp_policy_nz_request_duration_seconds`
- `nlp_policy_nz_errors_total`
- `nlp_policy_nz_active_requests`
- `nlp_policy_nz_model_loaded`

## Probes

- `/startup` reports initialization progress
- `/ready` reports pipeline and database readiness
- `/live` reports basic process liveness

## Degraded Mode

If the embedding model cannot be loaded:

- `/embed` returns `503` with `MODEL_NOT_LOADED`
- `/search` falls back to a deterministic keyword-only response and includes `X-Degraded: true`
- `/process` disables embedding generation and continues without embeddings

## Client SDK

The API client parses problem detail responses into typed errors so downstream code can branch on error codes instead of raw status text.
