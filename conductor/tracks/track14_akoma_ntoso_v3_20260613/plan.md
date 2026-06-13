# Track 14: Akoma-Ntoso v3 Schema Compliance & Enrichment

**Dependencies**: Track 4
**Parallelization Node**: Schema Standards Compliance
**Status**: Pending

---

## Phase 1: Schema Research & Validator

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Download OASIS AKN v3 XSD schemas | [ ] | |
| 1.2 | Create AKN XML validation utility | [ ] | |
| 1.3 | Audit existing emitter against v3 | [ ] | |
| 1.4 | Write schema validation tests | [ ] | |

## Phase 2: FRBR & Document Types

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Implement full FRBR hierarchy (4 levels) | [ ] | |
| 2.2 | Add amendment, judgment, bill, debate emitters | [ ] | |
| 2.3 | Implement TLCEvent and analysis metadata | [ ] | |
| 2.4 | Add references metadata for citations | [ ] | |

## Phase 3: CI Integration

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add AKN validation to CI pipeline | [ ] | |
| 3.2 | Create AKN output examples | [ ] | |
| 3.3 | Update design.md | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/schema/__init__.py` | Create |
| `src/nlp_policy_nz/schema/akn_v3.py` | Create |
| `src/nlp_policy_nz/universal_framework_v4.py` | Create |
| `tests/test_akn_v3.py` | Create |
