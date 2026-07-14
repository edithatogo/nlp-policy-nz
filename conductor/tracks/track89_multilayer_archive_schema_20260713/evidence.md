# Track 89 Evidence

## Implemented

- `nlp_policy_nz.archive.schema` defines versioned source, document, page, region, span, line, token, table, speech, embedding, assertion, graph-edge, and run models.
- Stable IDs, original/normalized coordinates, access classes, source checksums, review state, confidence, and referential-integrity validation are enforced before export.
- `public_projection()` removes restricted source text, OCR alternatives, and restricted embedding vectors while retaining safe lineage metadata.
- Deterministic JSON, JSONL, JSON-LD, RDF/Turtle, Markdown, and Parquet serializers are available.
- `migrate_bundle()` explicitly supports `0.9.0` to `1.0.0` and rejects unknown versions.

## Verification

- Track 89 contract tests: 6 passed, including a Hypothesis property test for stable IDs.
- Archive package coverage: 94.51%.
- `basedpyright src/nlp_policy_nz/archive`: 0 errors, 0 warnings, 0 notes.
- Ruff check and format checks passed.

## Boundaries

- The schema stores lineage and metadata but does not acquire corpus data or invent rights permissions.
- Public exports must be created from `public_projection()` when any source object is restricted.
- External dataset publication and cloud-scale materialization remain Tracks 90-91 responsibilities.
