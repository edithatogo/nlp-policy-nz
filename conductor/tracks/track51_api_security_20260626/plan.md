# Track 51: API Security & Authentication

**Dependencies**: Tracks 7, 45, 46
**Parallelization Node**: Security & Observability
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Add FastAPI dependency `verify_api_key` that checks `Authorization: Bearer <key>` against SHA-256 hashed key store | [ ] | conductor_orchestrator |
| 2 | Create key store module in `src/nlp_policy_nz/api/auth.py` with load/save/validate/rotate operations; key file stored in `config/api_keys.json` (gitignored) | [ ] | conductor_orchestrator |
| 3 | Add CLI subcommands `auth create-key`, `auth list-keys`, `auth revoke-key`, `auth rotate-key` with scope assignment | [ ] | conductor_orchestrator |
| 4 | Implement scope-based authorization: read/write/admin scopes enforced in endpoint dependencies; public exemption for `/health` | [ ] | conductor_orchestrator |
| 5 | Add structured JSON audit logging to `logs/api_audit.log` with rotation (RotatingFileHandler); instrument all middleware with before/after hooks | [ ] | conductor_orchestrator |
| 6 | Add security headers middleware: X-Content-Type-Options, Strict-Transport-Security, CORS restricted origins, request body size limits | [ ] | conductor_orchestrator |
| 7 | Add rate-limit response headers (`X-RateLimit-*`) per key, integrating with Track 46 slowapi rate limiter | [ ] | conductor_orchestrator |
| 8 | Write tests: unauthenticated returns 401, valid key with wrong scope returns 403, key CRUD operations, audit log entries verify | [ ] | conductor_orchestrator |
| 9 | Document API security in `docs/ops/api_security.md`: key generation, scopes, audit log interpretation, incident response | [ ] | conductor_orchestrator |

## Evidence Boundary

Auth middleware, key store module, CLI subcommands, audit log implementation, security headers, and tests satisfy repo-side evidence. Production key distribution and incident response require operational processes.
