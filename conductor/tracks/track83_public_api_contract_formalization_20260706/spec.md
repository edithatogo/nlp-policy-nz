# Track 83: Public API Contract Formalization

## Overview

Turn the existing FastAPI server and Python client SDK into a versioned public API surface. The focus is contract stability: OpenAPI, request/response models, auth scopes, RFC 7807 errors, examples, and SDK parity.

## Functional Requirements

- Map FastAPI endpoints and SDK methods to the Track 81 capability registry.
- Generate and pin a versioned OpenAPI artifact for public endpoints.
- Add compatibility tests for request/response models, RFC 7807 error payloads, auth scopes, health/version endpoints, and client SDK behavior.
- Document API lifecycle rules, versioning policy, deprecation policy, and environment expectations.
- Ensure sync and async clients expose the same supported capability set.
- Add examples for local server startup and representative search/process/report workflows.

## Non-Functional Requirements

- Contract tests must run locally and in GitHub Actions without external credentials.
- API schema generation must be deterministic.
- Auth and audit behavior must remain explicit for publishing, write, or external-network operations.
- The API must preserve graceful degradation for optional heavy dependencies.

## Acceptance Criteria

- [ ] Versioned OpenAPI artifact is generated, checked, and documented.
- [ ] API endpoint and SDK capability mapping is validated against Track 81.
- [ ] Contract tests cover success, auth, validation failure, RFC 7807 errors, and client SDK parity.
- [ ] API lifecycle, versioning, and deprecation policy are documented.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Production hosting changes.
- Adding new model-serving infrastructure.
- Replacing FastAPI.
