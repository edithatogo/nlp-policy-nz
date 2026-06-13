# Track 11: Temporal Expression Extraction & Time Ontology

**Dependencies**: Track 4, Track 5
**Parallelization Node**: Temporal Analysis
**Status**: Pending

---

## Phase 1: Pattern Library & Extractor

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Research NZ legislative temporal patterns: commencement dates, deadlines, durations in NZ Acts | [ ] | |
| 1.2 | Create `src/nlp_policy_nz/legal/temporal.py` with `TEMPORAL_PATTERNS` and `TemporalExtractor` component | [ ] | |
| 1.3 | Implement ISO 8601 normalization for extracted dates and durations | [ ] | |
| 1.4 | Write tests for temporal pattern matching and normalization | [ ] | |

## Phase 2: Temporal Relationship Graph

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `TemporalGraph` class for temporal event linking | [ ] | |
| 2.2 | Implement section-to-date linking using dependency parsing | [ ] | |
| 2.3 | Add temporal query methods (find_active_sections, effective_period) | [ ] | |
| 2.4 | Write tests for temporal relationship queries | [ ] | |

## Phase 3: Pipeline Integration

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `temporal_expressions` field to `PipelineRecord` | [ ] | |
| 3.2 | Update `process_legislation()` and `process_hansard()` | [ ] | |
| 3.3 | Update Parquet schema | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/legal/temporal.py` | Create |
| `src/nlp_policy_nz/legal/__init__.py` | Modify |
| `src/nlp_policy_nz/storage/serialization.py` | Modify |
| `src/nlp_policy_nz/api.py` | Modify |
| `tests/test_temporal.py` | Create |
