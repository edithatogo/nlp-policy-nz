# Vector Store Dependency Decision

Track 57 makes LanceDB the default vector-store backend for this repo and keeps other storage engines behind explicit optional or experimental boundaries.

## Decision

| Dependency | Status | Rationale |
|---|---|---|
| LanceDB | Required default | Current CLI, API, pipeline search, and RAG wrapper already use LanceDB as the local/serverless vector store. It fits the repo's Parquet/Arrow-oriented storage model and does not require a separate service. |
| Qdrant | Optional, remote-service only | The adapter is useful when a deployment explicitly needs Qdrant service semantics, but in-memory/local lifecycle behavior duplicates LanceDB coverage. Generic vector-backend behavior should be tested through LanceDB. |
| FAISS | Benchmark/dev optional | FAISS is useful for in-memory benchmark comparison, but it should not be installed by default for ordinary ingestion, extraction, API, or search workflows. |
| sqlite3 | Required via stdlib | Extraction catalogs can keep using Python's standard SQLite support for local manifests. |
| sqlite-utils | Remove unless justified | No current import path requires `sqlite-utils`; keeping it as a default dependency adds install surface without runtime value. |
| DuckDB VSS | Experimental analytics candidate | DuckDB may be useful for SQL analytics over Parquet and vector arrays, but it should be evaluated in a follow-up analytics track rather than replacing LanceDB. |
| RocksDB | Rejected/deferred | RocksDB is an embedded key-value store. It does not replace Parquet artifacts, LanceDB vector search, or SQLite-style manifest catalogs for this repo's current abstractions. |

## Qdrant Boundary

Generic behavior that should be covered by LanceDB tests:

- create or overwrite a local index
- reject empty index creation
- add records after index creation
- search returns `doc_id`, `text`, and `score`
- empty or deleted index returns no results
- delete index lifecycle
- reopen a persisted index through a fresh adapter instance
- fail closed to an empty index state when a persisted table cannot be opened

## Comparison Threshold

Qdrant remains optional unless it beats the shared LanceDB benchmark fixture by
at least 10% on mean search or update latency at the same recall proxy, while
preserving the lifecycle behavior above. If it does not clear that bar, the
local LanceDB path stays the default and Qdrant remains remote-service only.

Qdrant-specific behavior that can justify optional tests:

- remote Qdrant URL or service deployment
- Qdrant collection configuration and vector distance model choices
- Qdrant client connection lifecycle
- payload semantics unique to Qdrant

## Follow-Up

Track 57 moved FAISS out of default Pixi dependencies, removed unjustified `sqlite-utils` declarations, and kept Qdrant import-safe without exporting it as part of the default storage surface.
