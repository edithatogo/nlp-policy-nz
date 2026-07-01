# Track 6 Evidence - Output Schema and LanceDB Vector Engine

Track 6 is complete for repo-side storage and vector-search scaffolding.

Implemented surfaces:

- `src/nlp_policy_nz/storage/serialization.py` provides `PipelineRecord`, `SCHEMA_FIELDS`, dataframe conversion, Parquet serialization, and Parquet loading helpers.
- `src/nlp_policy_nz/storage/vectordb.py` provides the default LanceDB adapter for local vector index lifecycle and search operations.
- `src/nlp_policy_nz/storage/__init__.py` exposes the stable storage API while keeping optional vector backends lazy.

Validation evidence:

- `tests/test_storage.py` covers `PipelineRecord`, schema ordering, dataframe conversion, Parquet round trips, optional fields, and committee/submission/regulations-review fields.
- `tests/test_vectordb.py` covers LanceDB initialization, empty create rejection, create/search, append, search-before-create, delete, overwrite, and distance-to-score conversion.
- `tests/test_storage_exports.py` covers storage package export behavior.
- The Track 6 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Full-corpus storage scale testing remains a later benchmark/observability concern.
- Production backup, restore, and service deployment maturity belongs to later production-hardening tracks.
