# Track 61: Unstructured Ingestion Adapter Evaluation

- [x] Confirm the existing ingestion boundary and choose the smallest valid
  integration point.
- [x] Implement an optional `UnstructuredIngestionEngine` that partitions
  local files and emits `DocumentChunk` records with provenance metadata.
- [x] Add tests for successful partitioning, missing dependency behavior, and
  missing file handling.
- [x] Update packaging metadata to expose an optional `unstructured` extra and
  a Pixi feature for opt-in use.
- [x] Update the product, requirements, tech stack, and dependency policy docs
  to state that `unstructured` is fallback-only.
- [x] Update the Conductor registry and GitHub mirror to reflect the completed
  track.
- [x] Validate the touched files with focused tests and repository checks.
- [x] Record evidence and mark the track complete.
