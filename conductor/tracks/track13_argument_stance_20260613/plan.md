# Track 13: Argument Mining & Policy Stance Detection

**Dependencies**: Track 5, Track 7
**Parallelization Node**: Discourse Analysis
**Status**: Pending

---

## Phase 1: Argument Component Detection

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Annotate 500 Hansard speech segments for argument components (premise, conclusion, none) | [ ] | |
| 1.2 | Fine-tune Legal-BERT for argument component sequence classification | [ ] | |
| 1.3 | Create `src/nlp_policy_nz/discourse/argument.py` with argument detector | [ ] | |
| 1.4 | Write tests for component detection | [ ] | |

## Phase 2: Stance Classification & Argument Graph

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Annotate 500 speech segments for stance (pro/con/neutral) | [ ] | |
| 2.2 | Fine-tune stance classifier on annotated debate data | [ ] | |
| 2.3 | Implement ArgumentGraph with support/attack relations | [ ] | |
| 2.4 | Add issue-argument linking via semantic similarity | [ ] | |

## Phase 3: Pipeline Integration

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `arguments` and `stance` fields to PipelineRecord | [ ] | |
| 3.2 | Update process_hansard() to run argument mining | [ ] | |
| 3.3 | Update Parquet schema | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/nlp_policy_nz/discourse/__init__.py` | Create |
| `src/nlp_policy_nz/discourse/argument.py` | Create |
| `src/nlp_policy_nz/discourse/stance.py` | Create |
| `src/nlp_policy_nz/cli/graph.py` | Modify |
| `src/nlp_policy_nz/api.py` | Modify |
| `tests/test_argument.py` | Create |
| `tests/test_stance.py` | Create |
