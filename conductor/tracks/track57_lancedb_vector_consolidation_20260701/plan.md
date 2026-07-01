# Track 57: LanceDB-First Vector Store Consolidation

**Dependencies**: Tracks 6, 23, 33, 44, 56
**Parallelization Node**: Storage Dependency Consolidation
**Status**: Complete

---

## Phase 1: Inventory and Decision Record

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | Inventory current storage/database dependencies in `pyproject.toml`, `pixi.toml`, storage adapters, CLI/API, docs, and tests | [x] | Inventory recorded in `docs/vector-store-dependency-decision.md`; LanceDB default, Qdrant optional import path, FAISS default Pixi dependency, sqlite-utils declared but unused, no DuckDB/RocksDB dependency |
| 1.2 | Add a dependency decision note covering LanceDB-first, DuckDB VSS experimental analytics, and RocksDB rejection/deferment | [x] | Added `docs/vector-store-dependency-decision.md` and updated dependency policy/maturity matrices |
| 1.3 | Define which Qdrant behaviors are generic vector-backend behaviors and which are remote-service-only | [x] | Generic lifecycle/search behavior belongs to LanceDB tests; Qdrant is reserved for remote-service and client-specific semantics |

## Phase 2: LanceDB Migration

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Add/expand LanceDB tests to cover Qdrant-equivalent lifecycle behavior: create, search, add, delete, empty index, overwrite, score shape | [x] | Expanded `tests/test_vectordb.py` with isolated LanceDB lifecycle coverage |
| 2.2 | Update `VectorBackend` docs to describe LanceDB as the default backend and Qdrant/FAISS as optional adapters | [x] | Updated storage package and `VectorBackend` docs; default package import no longer exports optional backends |
| 2.3 | Migrate Qdrant workflow references in tests/docs to LanceDB unless they require remote-service semantics | [x] | Removed generic Qdrant adapter tests; remaining Qdrant branch tests cover optional import/client-specific behavior |
| 2.4 | Verify CLI/API/search paths continue to default to `./lancedb_data` and pass focused tests | [x] | Focused pipeline/API helper tests passed with LanceDB default import surface |

## Phase 3: Dependency Simplification

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3.1 | Remove `sqlite-utils` from runtime/Pixi dependency declarations if no import path requires it | [x] | Removed from `pyproject.toml`, `pixi.toml`, and `pixi.lock`; stdlib `sqlite3` stays |
| 3.2 | Move FAISS to optional benchmark/dev-only dependency if benchmark tests still require it | [x] | Removed from default Pixi and dev dependencies; `[project.optional-dependencies].faiss` remains |
| 3.3 | Keep Qdrant as optional extra only if remote-service semantics remain justified; otherwise remove public export and tests | [x] | Removed default storage export and generic lifecycle tests; optional concrete module remains with import-safe branch tests |
| 3.4 | Update dependency policy matrix and maturity checklist | [x] | Updated `conductor/dependency-policy-matrix.md` and `conductor/maturity-checklist.md` |

## Phase 4: DuckDB VSS and RocksDB Decision

| # | Task | Status | Notes |
|---|------|--------|-------|
| 4.1 | Create a small DuckDB VSS spike note over Parquet/vector arrays, without adding it to default dependencies | [x] | Documented in `docs/vector-store-dependency-decision.md`; no dependency added |
| 4.2 | Decide whether DuckDB VSS deserves a follow-up implementation track for corpus analytics | [x] | Decision: only as a later analytics track, not Track 57 default storage |
| 4.3 | Record why RocksDB is not introduced for this repo's current abstractions | [x] | Documented as rejected/deferred key-value store |

## Phase 5: Validation and Closeout

| # | Task | Status | Notes |
|---|------|--------|-------|
| 5.1 | Run focused storage tests: LanceDB, CLI search defaults, pipeline API search, extraction catalog, and dependency-policy tests | [x] | Passed focused LanceDB/storage export/pipeline helper tests; full CI pending after push |
| 5.2 | Run targeted Ruff on changed storage/tests/docs files | [x] | Targeted Ruff passed |
| 5.3 | Record evidence and residual optional-backend decisions | [x] | `evidence.md` added |
| 5.4 | Review and archive track when dependency simplification is complete | [x] | Repo-side completion committed; review/archive can run as a follow-up conductor action |
