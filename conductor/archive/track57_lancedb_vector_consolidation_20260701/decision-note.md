# Track 57 Decision Note: LanceDB-First Vector Consolidation

## Decision

Use LanceDB as the only required vector-store backend for local, CI, API, CLI,
and RAG workflows. Keep Qdrant and FAISS behind explicit optional imports and
extras. Remove dependencies that are not used by runtime imports.

## Rationale

- LanceDB is already the default vector database in the CLI, API, pipeline API,
  and Haystack-style retrieval wrapper.
- Generic vector-store lifecycle behavior can be covered locally with LanceDB:
  create, search, add, delete, empty search, overwrite, and score shape.
- Qdrant only adds value when a remote vector service is explicitly required.
  Its in-memory behavior duplicates the default LanceDB test surface.
- FAISS remains useful for benchmarks, but it should not be part of the default
  Pixi environment because wheel availability and native packaging can slow CI.
- DuckDB VSS is worth evaluating as an experimental analytics path over
  Parquet/vector arrays, but it should not replace LanceDB as the production
  vector backend in this track.
- RocksDB is a low-level embedded key-value store. It does not replace Parquet
  corpus artifacts, LanceDB vector search, or stdlib SQLite extraction catalogs.
- `sqlite-utils` has no import path in the repo. The extraction catalog uses
  Python stdlib `sqlite3`, so the dependency is removed.

## Qdrant Behavior Classification

| Behavior | Classification | Track 57 Action |
|---|---|---|
| Create local collection/index | Generic vector lifecycle | Covered by LanceDB tests |
| Search by query vector | Generic vector lifecycle | Covered by LanceDB tests |
| Add records after index creation | Generic vector lifecycle | Covered by LanceDB tests |
| Delete collection/index | Generic vector lifecycle | Covered by LanceDB tests |
| Search before creation returns empty | Generic vector lifecycle | Covered by LanceDB tests |
| Overwrite existing index | Generic vector lifecycle | Covered by LanceDB tests |
| Remote Qdrant server URL/location | Remote-service-specific | Keep optional behind `qdrant` extra |
| Qdrant collection API and payload mapping | Adapter-specific | Keep focused optional adapter branch tests |

## Follow-Up Candidate

Create a later DuckDB VSS analytics track only if corpus analytics need SQL over
Parquet-backed vectors in the shared NLP engine. Until then, DuckDB VSS should
remain out of default dependencies.
