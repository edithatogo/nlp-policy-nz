# Track 86 Specification: HathiTrust-NZ Ingestion Contract

## Goal

Create a fail-closed, versioned contract that imports HathiTrust-NZ archive-registry and source-manifest rows into `nlp-policy-nz` without downloading corpus content locally.

## Requirements

- Validate collection, dataset, volume, source object, rights, acquisition, and publication fields with frozen Pydantic schemas.
- Preserve the 510-row curated Hansard seed as a named cohort distinct from expanded discovery.
- Resolve immutable source/checksum identifiers and reject content jobs lacking affirmative publication eligibility.
- Emit deterministic work manifests partitioned for cloud execution and resumable by content hash.
- Add CLI/API/MCP-compatible capability registration, JSON Schema, fixtures, and migration documentation.
- Test malformed rights states, duplicate HTIDs, count drift, source substitution, and restricted-content routing.

## Out Of Scope

OCR execution and publication are handled by dependent tracks.

## Acceptance

Contract tests exceed 90% coverage for new modules; strict typing, linting, security, and schema compatibility gates pass.
