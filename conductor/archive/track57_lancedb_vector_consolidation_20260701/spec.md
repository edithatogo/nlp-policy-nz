# Track 57: LanceDB-First Vector Store Consolidation

**Dependencies**: Tracks 6, 23, 33, 44, 56
**Parallelization Node**: Storage Dependency Consolidation
**Status**: Complete

---

## Goal

Reduce storage/search dependency sprawl by making LanceDB the single default vector-store backend for local, CI, API, and RAG workflows, while keeping experimental or service-oriented alternatives behind explicit optional gates.

## Context

The repo currently has:

- Parquet/PyArrow/Polars/Narwhals as the canonical structured corpus storage layer.
- LanceDB as the default local vector database at `./lancedb_data`.
- Qdrant adapter and tests for optional in-memory/local/remote vector service semantics.
- FAISS adapter and benchmarks for in-memory vector index comparisons.
- SQLite via Python `sqlite3` for extraction manifest catalogs.
- `sqlite-utils` declared as a dependency, but no current import path requires it.
- No DuckDB dependency yet; existing Conductor notes mark DuckDB as not applicable to the shared NLP engine.

Official docs reviewed on 2026-07-01:

- LanceDB supports vector search plus full-text/hybrid search and filtering, matching this repo's local-first retrieval needs.
- DuckDB VSS is explicitly experimental, but useful enough to evaluate for analytical SQL over Parquet/vector arrays.
- RocksDB is an embedded key-value store, not a direct fit for this repo's Parquet/vector/search abstractions.

## Scope

- Make LanceDB the only required vector-store backend in default runtime dependencies.
- Migrate Qdrant workflow coverage to LanceDB-equivalent tests where the behavior is local search/index lifecycle rather than remote-service semantics.
- Preserve a narrow optional Qdrant contract only if a concrete remote service requirement is documented.
- Demote FAISS from default Pixi dependencies into an optional benchmark/dev extra if benchmarks still need it.
- Remove `sqlite-utils` unless a real `sqlite-utils` import path is introduced; retain stdlib `sqlite3` for extraction catalogs.
- Evaluate DuckDB VSS as an experimental Track 57 sub-decision for analytics over Parquet/vector artifacts, not as the default vector DB.
- Document why RocksDB is not introduced.

## Acceptance Criteria

- [x] Dependency matrix is updated to mark LanceDB required, Qdrant optional/deprecated, FAISS benchmark-only optional, DuckDB VSS experimental, RocksDB rejected/deferred, and `sqlite-utils` removed or justified.
- [x] Qdrant test coverage is replaced by LanceDB-equivalent behavior tests where no remote-service-only feature is being tested.
- [x] Qdrant adapter is either removed from public exports or marked optional/deprecated with import-safe behavior and clear tests.
- [x] FAISS is no longer installed by default in Pixi unless a benchmark gate proves it should stay.
- [x] `sqlite-utils` is removed from dependency declarations unless a real import path requires it.
- [x] Focused local validation passes without requiring Qdrant or FAISS packages; full hosted CI remains a post-push check.
- [x] DuckDB VSS evaluation note records whether to add a later dedicated DuckDB analytics track.
- [x] Search/API/RAG paths still use LanceDB successfully.

## Non-Goals

- Do not replace Parquet as the canonical corpus artifact format.
- Do not make DuckDB VSS the production vector store in this track.
- Do not add RocksDB bindings.
- Do not remove stdlib SQLite extraction catalogs unless a superior catalog replacement is implemented and tested.
