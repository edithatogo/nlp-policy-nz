# Track 89 Plan

**Status**: core schema milestone complete; expanded assurance transferred to Track 97 / issue #133

## Phase 1: Canonical model

- [x] Implement the versioned schema, stable IDs, coordinates, provenance, and referential integrity.
- [x] Add deterministic contract and property tests.

## Phase 2: Views and effective access

- [x] Implement JSON, JSONL, JSON-LD, RDF, Markdown, Parquet, graph, and migration surfaces.
- [x] Fix public projection so restricted access propagates transitively from source objects through all descendants and referencing objects.
- [x] Add cross-serializer restricted-content canary coverage.

## Phase 3: Milestone assurance and transfer

- [x] Run focused schema, serializer, lint, and type checks.
- [x] Record the independent panel's restricted-descendant finding and regression fix.
- [x] Transfer exhaustive mixed-access, mutation, compatibility, serializer, rights-basis, and performance assurance to Track 97 / issue #133.
