# Track 89 Evidence

## Implemented

- `nlp_policy_nz.archive.schema` defines versioned source, document, page, region, span, line, token, table, speech, embedding, assertion, graph-edge, and run models.
- Stable IDs, original/normalized coordinates, access classes, source checksums, review state, confidence, and referential-integrity validation are enforced before export.
- `public_projection()` removes restricted source text, OCR alternatives, and restricted embedding vectors while retaining safe lineage metadata.
- Deterministic JSON, JSONL, JSON-LD, RDF/Turtle, Markdown, and Parquet serializers are available.
- `migrate_bundle()` explicitly supports `0.9.0` to `1.0.0` and rejects unknown versions.

## Verification

- Track 89 contract tests: 6 passed, including a Hypothesis property test for stable IDs.
- Track 89 review tests: 8 passed, including inherited-rights redaction and run-output integrity.
- Archive package coverage: 93.00%.
- `basedpyright src/nlp_policy_nz/archive`: 0 errors, 0 warnings, 0 notes.
- Ruff check and format checks passed.
- Serializer smoke timing: 100 JSONL writes of a minimal bundle completed in 0.1102 seconds on the local runner.
- Mutation tooling residual: the bounded `mutatest 3.1.0` run discovered 114 candidate locations but failed before trials with `TypeError: Population must be a sequence`; this is an upstream tool/runtime incompatibility, not a surviving mutant result.

## Boundaries

- The schema stores lineage and metadata but does not acquire corpus data or invent rights permissions.
- Public exports must be created from `public_projection()` when any source object is restricted.
- External dataset publication and cloud-scale materialization remain Tracks 90-91 responsibilities.

## Review Fixes

- Restricted access now propagates from sources through documents, pages, regions, spans, lines, tokens, speeches, tables, embeddings, and assertions.
- All serializers default to the public projection; raw restricted serialization requires explicit `public=False`.
- Added original-to-normalized coordinate conversion and public span-length validation.
- Run output identifiers are now checked for referential integrity.
