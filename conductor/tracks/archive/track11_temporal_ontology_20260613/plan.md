# Track 11: Temporal Expression Extraction & Time Ontology

**Dependencies**: Track 4, Track 5
**Parallelization Node**: Temporal Analysis
**Status**: Completed

**Archived**: 2026-06-22 after focused temporal/storage verification passed.

---

## Phase 1: Pattern Library & Extractor

**Status**: Completed

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Research NZ legislative temporal patterns: commencement dates, deadlines, durations in NZ Acts | [x] | |
| 1.2 | Create `src/nlp_policy_nz/legal/temporal.py` with `TEMPORAL_PATTERNS` and `TemporalExtractor` component | [x] | |
| 1.3 | Implement ISO 8601 normalization for extracted dates and durations | [x] | |
| 1.4 | Write tests for temporal pattern matching and normalization | [x] | |

## Phase 2: Temporal Relationship Graph

**Status**: Completed

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `TemporalGraph` class for temporal event linking | [x] | |
| 2.2 | Implement section-to-date linking using dependency parsing | [x] | |
| 2.3 | Add temporal query methods (find_active_sections, effective_period) | [x] | |
| 2.4 | Write tests for temporal relationship queries | [x] | |

## Phase 3: Pipeline Integration

**Status**: Completed

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `temporal_expressions` field to `PipelineRecord` | [x] | |
| 3.2 | Update `process_legislation()` and `process_hansard()` | [x] | |
| 3.3 | Update Parquet schema | [x] | |
| 3.4 | Run full test suite | [x] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/legal/temporal.py` | Create |
| `src/nlp_policy_nz/legal/__init__.py` | Modify |
| `src/nlp_policy_nz/storage/serialization.py` | Modify |
| `src/nlp_policy_nz/pipeline_api.py` | Modify |
| `src/nlp_policy_nz/api/server.py` | Modify |
| `tests/test_temporal.py` | Create |

## Implementation Evidence

- `python -m pytest tests\test_temporal.py -p no:cacheprovider -q` -> 7 passed.
- `python -m pytest tests\test_storage.py -p no:cacheprovider -q` -> 16 passed.
- `python -m coverage run --data-file=.tmp\coverage\track11.coverage -m pytest tests\test_temporal.py -p no:cacheprovider -q && python -m coverage report --data-file=.tmp\coverage\track11.coverage --include=src\nlp_policy_nz\legal\temporal.py -m` -> 93% coverage for `temporal.py`.
- `python -m ruff check --no-cache src\nlp_policy_nz\legal\temporal.py src\nlp_policy_nz\legal\__init__.py tests\test_temporal.py` -> passed.
- `python -m py_compile src\nlp_policy_nz\pipeline_api.py src\nlp_policy_nz\api\server.py` -> passed.
- `python -m pytest -p no:cacheprovider -q` -> 459 passed, 1 warning.
