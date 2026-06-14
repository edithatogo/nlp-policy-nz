# Track 10: Deontic Modality & Legal Effect Classification

**Dependencies**: Track 4, Track 5
**Parallelization Node**: Legal Effect Analysis
**Status**: Pending

---

## Phase 1: Pattern Design & Component Scaffold

**Estimated Effort**: Medium
**Status**: Pending

- [ ] **Task 1.1: Research NZ legislative modality patterns**
  - Analyse 50 NZ Acts for "must", "shall", "may", "must not", "shall not", "need not" usage.
- [ ] **Task 1.2: Create modality module**
  - Create `src/nlp_policy_nz/legal/modality.py` with `DEONTIC_PATTERNS` dictionary and `DeonticModalityDetector` spaCy component.
- [ ] **Task 1.3: Implement modality scope resolution**
  - Use spaCy dependency tree to identify the governed verb/clause for resolved modalities.
- [ ] **Task 1.4: Write unit tests**
  - Write unit tests for pattern matching and scope resolution in `tests/test_modality.py`.

---

## Phase 2: Legal Effect Classification

**Estimated Effort**: Medium
**Status**: Pending

- [ ] **Task 2.1: Define LegalEffect categories**
  - Define `LegalEffect` enum with LKIF categories (obligation, prohibition, permission, power, liability, immunity, disability).
- [ ] **Task 2.2: Implement rule-based legal effect classifier**
  - Implement a rule-based legal effect classifier for legislative sections in `src/nlp_policy_nz/legal/effects.py`.
- [ ] **Task 2.3: Integrate section-level classification**
  - Add `classify_legal_effect()` to section-level chunking pipeline.
- [ ] **Task 2.4: Write tests for classification**
  - Write tests for classification accuracy on annotated NZ legislation in `tests/test_legal_effects.py`.

---

## Phase 3: Pipeline Integration

**Estimated Effort**: Low-Medium
**Status**: Pending

- [ ] **Task 3.1: Add deontic fields to serialization**
  - Add `deontic_modality` and `legal_effect` fields to `PipelineRecord` in `storage/serialization.py`.
- [ ] **Task 3.2: Update legislation processor**
  - Update `process_legislation()` in `api.py` to run modality detector.
- [ ] **Task 3.3: Update Parquet schema**
  - Update Parquet schema and serializer to include new fields.
- [ ] **Task 3.4: Run full verification**
  - Run full test suite and fix any regressions.
