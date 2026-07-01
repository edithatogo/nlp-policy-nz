# Track 57 Evidence: LanceDB-First Vector Store Consolidation

## Phase 1 Inventory

- `lancedb` is a runtime and Pixi dependency and is used by `LanceDBAdapter`, pipeline search, CLI search defaults, API search paths, and the Haystack-compatible RAG wrapper.
- `qdrant-client` is not a default dependency, but `QdrantAdapter` exists and already fails import-safely when the optional client is missing.
- `faiss-cpu` is declared in Pixi default dependencies and as a dev/optional extra in `pyproject.toml`; current use is adapter tests and benchmark comparisons.
- `sqlite-utils` is declared in runtime/Pixi dependencies, but repository search found no import path requiring it. Stdlib `sqlite3` remains available for extraction catalogs.
- DuckDB is not currently declared as a dependency. Track 57 treats DuckDB VSS as an experimental analytics candidate over Parquet/vector arrays.
- RocksDB is not declared and is rejected/deferred for current repo abstractions.

## Decision Artifacts

- Added `docs/vector-store-dependency-decision.md`.
- Added `conductor/tracks/track57_lancedb_vector_consolidation_20260701/decision-note.md`.
- Updated `conductor/dependency-policy-matrix.md`.
- Updated `conductor/maturity-checklist.md`.

## Qdrant Boundary

Generic vector lifecycle behavior belongs to LanceDB coverage: create, overwrite, empty-create rejection, add, search result shape, delete, and empty/deleted search behavior.

Qdrant coverage should remain only for remote-service or client-specific semantics: remote URL/service configuration, collection-specific settings, payload behavior, and connection lifecycle.

## Implemented Dependency Simplification

- Removed `sqlite-utils` from `pyproject.toml`, `pixi.toml`, and `pixi.lock`.
- Removed `faiss-cpu` from default Pixi and dev dependencies while keeping the `faiss` optional extra.
- Removed `FAISSAdapter` and `QdrantAdapter` from the default `nlp_policy_nz.storage` export surface.
- Added LanceDB lifecycle tests covering create, search, add, delete, empty index, overwrite, and score shape.
- Updated LanceDB search `score` to be higher-is-better while preserving `_distance` for compatibility.

## Validation

- `pixi run pytest tests/test_vectordb.py tests/test_storage_exports.py tests/test_cli.py::TestSearchSubcommand tests/test_extraction_catalog.py tests/test_qdrant_adapter_branches.py tests/test_faiss_adapter.py -q`
  - Result: 22 passed, 1 skipped, 1 warning.
- `pixi run ruff check src\nlp_policy_nz\storage\__init__.py src\nlp_policy_nz\storage\interfaces.py src\nlp_policy_nz\storage\vectordb.py tests\test_vectordb.py tests\test_storage_exports.py tests\test_qdrant_adapter_branches.py`
  - Result: all checks passed.
- `uv lock --check`
  - Result: lockfile is current.
- `pixi lock`
  - Result: lockfile already up to date after manifest changes.

## Residual Work

- Full hosted CI should be checked after push.

## Review Fixes

- Preserved root-level optional adapter compatibility through lazy `__getattr__`
  resolution without eager FAISS/Qdrant imports.
- Changed LanceDB score conversion to `-distance` so it preserves
  lower-is-better ordering without assuming nonnegative L2-style distances.
- Added tests for root import compatibility, missing optional backend imports,
  Qdrant constructor defaults, and distance-to-score conversion.
- Corrected Conductor wording so local focused validation is not overstated as
  hosted CI completion.
