# Track 60 Evidence

## Summary

Track 60 hardens LanceDB as the default local retrieval backend and records the
supported lifecycle, comparison threshold, and GitHub mirror state.

## Implementation Notes

- `src/nlp_policy_nz/storage/vectordb.py`
  - `close()` now releases the adapter handle without deleting persisted data.
  - `_open_or_create_table()` now falls back to an empty safe state when an
    existing LanceDB table cannot be opened.
  - `delete_index()` and `index_exists()` now guard against a released adapter.
- `tests/test_vectordb.py`
  - Added reopen coverage for a persisted table.
  - Added corruption-safe reopen coverage.
- `tests/benchmarks/test_vector_benchmark.py`
  - Added update-latency and recall-proxy benchmark coverage.
- `docs/vector-store-dependency-decision.md`
  - Added the supported lifecycle and explicit Qdrant promotion threshold.
- `src/nlp_policy_nz/pipeline_api.py` and `src/nlp_policy_nz/api/server.py`
  - Updated search entrypoint docs to describe the supported LanceDB lifecycle.

## Validation

- `python -m pytest tests/test_vectordb.py tests/benchmarks/test_vector_benchmark.py -q`
  - Passed: `12 passed, 1 skipped`
- `python -m ruff check src/nlp_policy_nz/storage/vectordb.py src/nlp_policy_nz/pipeline_api.py src/nlp_policy_nz/api/server.py tests/test_vectordb.py tests/benchmarks/test_vector_benchmark.py`
  - Passed with no lint findings.

## GitHub Mirror

- GitHub issue `#62` exists and is open as `Track 60: LanceDB Retrieval Runtime
  Hardening`.
- The issue is present in GitHub Projects `#3` and `#4`.

## Residual Notes

- The issue acceptance criteria are satisfied locally. The track stays in the
  registry as a completed track until review or archive cleanup is requested.
