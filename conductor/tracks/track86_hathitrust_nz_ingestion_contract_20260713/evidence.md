# Track 86 Evidence

## Implemented

- `src/nlp_policy_nz/extraction/hathi_ingestion.py` provides frozen Pydantic contracts for registry datasets, archive items, publication decisions, work items, and deterministic shards.
- Public full-text work requires `public_full_text` access, an explicit SHA-256 digest, and a non-restricted digitization profile. Restricted profiles fail closed to metadata-only.
- Existing Hathi labels are normalized, including `public_full_text_where_confirmed` and `metadata_only_until_static_host_bundle_is_eligible`.
- `data/track86/hathi_capability_registry.json` registers read-only CLI, API, SDK, and MCP capability metadata.
- The live Hathi-NZ registry loaded successfully with collection `hathitrust-nz`, source collection `71329709`, seed count `510`, and five datasets.

## Verification

- `tests/test_hathi_ingestion.py`: 18 passed.
- Track 86 module coverage: 100% statements and branches covered by the focused test run.
- `basedpyright src/nlp_policy_nz/extraction/hathi_ingestion.py`: 0 errors, 0 warnings, 0 notes.
- Ruff check and format checks passed for the implementation and tests.
- Selected broader extraction and Conductor tests: 36 passed.
- Repository-wide pytest: 1,015 passed, 3 skipped, 25 pre-existing failures outside Track 86. Those failures concern stale archived-track paths, unrelated fixture drift, Gradio artifacts, storage field expectations, and workflow/container assertions.

## Boundary

This track validates and plans metadata only. It does not acquire corpus payloads or publish data. Cloud acquisition and publication remain the responsibility of Tracks 87, 90, and 91.
