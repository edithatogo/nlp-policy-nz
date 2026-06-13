# Track 10: Deontic Modality & Legal Effect Classification

**Dependencies**: Track 4, Track 5
**Parallelization Node**: Legal Effect Analysis
**Status**: Pending

---

## Phase 1: Pattern Design & Component Scaffold

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Research NZ legislative modality patterns: analyse 50 NZ Acts for "must", "shall", "may", "must not", "shall not", "need not" usage | [ ] | |
| 1.2 | Create `src/nlp_policy_nz/legal/modality.py` with `DEONTIC_PATTERNS` dictionary and `DeonticModalityDetector` spaCy component | [ ] | |
| 1.3 | Implement modality scope resolution using spaCy dependency tree (identify governed verb/clause) | [ ] | |
| 1.4 | Write unit tests for pattern matching and scope resolution | [ ] | |

## Phase 2: Legal Effect Classification

**Estimated Effort**: Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Define `LegalEffect` enum with LKIF categories (obligation, prohibition, permission, power, liability, immunity, disability) | [ ] | |
| 2.2 | Implement rule-based legal effect classifier for legislative sections | [ ] | |
| 2.3 | Add `classify_legal_effect()` to section-level chunking pipeline | [ ] | |
| 2.4 | Write tests for classification accuracy on annotated NZ legislation | [ ] | |

## Phase 3: Pipeline Integration

**Estimated Effort**: Low-Medium
**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `deontic_modality` and `legal_effect` fields to `PipelineRecord` in `storage/serialization.py` | [ ] | |
| 3.2 | Update `process_legislation()` in `api.py` to run modality detector | [ ] | |
| 3.3 | Update Parquet schema to include new fields | [ ] | |
| 3.4 | Run full test suite and fix any regressions | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/legal/__init__.py` | Create |
| `src/nlp_policy_nz/legal/modality.py` | Create |
| `src/nlp_policy_nz/legal/effects.py` | Create |
| `src/nlp_policy_nz/storage/serialization.py` | Modify |
| `src/nlp_policy_nz/api.py` | Modify |
| `tests/test_modality.py` | Create |
| `tests/test_legal_effects.py` | Create |
