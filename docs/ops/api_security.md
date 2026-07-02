# API Security

## Overview

The FastAPI server requires API keys for all data endpoints. Public health and version routes remain open so orchestration and readiness checks can run without credentials.

## API Keys

- Store path: `config/api_keys.json`
- Secret format: generated server-side, stored only in hashed form
- Supported headers:
  - `Authorization: Bearer <key>`
  - `X-API-Key: <key>`

## Scopes

- `read`: `/embed`, `/search`
- `write`: `/process`
- `admin`: key lifecycle commands and future operational endpoints

## CLI

Use the `auth` command group to manage keys:

```bash
nlp-policy-nz auth create-key --name "service" --scopes read write
nlp-policy-nz auth list-keys
nlp-policy-nz auth revoke-key --key-id <key_id>
nlp-policy-nz auth rotate-key --key-id <key_id>
```

## Audit Log

- Path: `logs/api_audit.log`
- Format: JSON lines
- Fields include timestamp, key hash, endpoint, method, status, duration, and client IP
- Failed authentication attempts are logged with the same structure so incident review has a single source of truth

## Incident Response

1. Revoke the compromised key.
2. Rotate any dependent secrets or deployment credentials.
3. Inspect `logs/api_audit.log` for the affected key hash and time window.
4. Mint a replacement key with the minimum scope needed.

## Operational Notes

- Keep `config/api_keys.json` out of version control.
- Rotate audit logs with the built-in `RotatingFileHandler`.
- Enforce TLS in production so the `Strict-Transport-Security` header is meaningful.
