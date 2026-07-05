# Track 51: API Security & Authentication

**Dependencies**: Tracks 7, 45, 46
**Parallelization Node**: Security & Observability
**Status**: Planned

## Goal

Add production-grade authentication, authorization, and audit logging to the FastAPI server so that API consumers are authenticated, operations are audited, and keys can be managed through their lifecycle.

## Scope

### 1. API Key Authentication
- FastAPI middleware or dependency that reads `Authorization: Bearer <key>` header
- Key validation against a store (env var, file, or DB)
- `X-API-Key` header support as alternative
- Public endpoints (health) exempt from auth; all data endpoints protected
- Rate limit scoped per-key (integration with Track 46 rate limiting)

### 2. Key Lifecycle Management
- CLI command `nlp-policy-nz auth create-key` to generate new keys
- CLI commands for list, revoke, rotate keys
- Key hashing (SHA-256) so plaintext keys are never stored
- Key metadata: name, scopes, created_at, expires_at, last_used
- Key storage: JSON file in `config/api_keys.json` (gitignored) or env-var

### 3. Scope-Based Authorization
- Read scope: `/embed`, `/search` endpoints
- Write scope: `/process` endpoint, pipeline execution
- Admin scope: key management, system operations
- Scope enforcement in FastAPI dependency

### 4. Audit Logging
- Log every authenticated request: timestamp, key hash, endpoint, method, status, duration
- Structured JSON audit log to `logs/api_audit.log` (with rotation)
- Audit log integrity: append-only with periodic rotation
- Failed authentication attempts logged with IP, endpoint, timestamp

### 5. Security Headers & Middleware
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security` (when served over HTTPS)
- CORS restricted to configured origins
- Request body size limits per-endpoint
- Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)

## Acceptance Criteria

- [ ] All data endpoints return 401 if no valid API key provided
- [ ] `/health` returns 200 without auth
- [ ] CLI `auth create-key` generates valid key; `auth revoke-key` revokes it
- [ ] Keys with read scope can call `/embed` and `/search` but not `/process`
- [ ] Audit log captures all authenticated requests with key hash and status
- [ ] Failed auth attempts logged with source IP
- [ ] Security headers present on all responses
- [ ] Rate limit headers returned on all authenticated responses
