# Track 12: Named Entity Resolution & Wikidata Linking

**Dependencies**: Track 5
**Parallelization Node**: Knowledge Base Integration
**Status**: Pending

---

## Phase 1: Knowledge Base Construction

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Create `src/nlp_policy_nz/kb/` module with entity schema | [ ] | |
| 1.2 | Compile KB entries for MPs, parties, electorates, ministries, courts | [ ] | |
| 1.3 | Include Wikidata QIDs for each entry | [ ] | |
| 1.4 | Write KB loading and query tests | [ ] | |

## Phase 2: Entity Resolution

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Implement `EntityResolver` with fuzzy matching | [ ] | |
| 2.2 | Add context disambiguation (party, date range) | [ ] | |
| 2.3 | Implement Wikidata SPARQL enrichment | [ ] | |
| 2.4 | Write resolution accuracy tests | [ ] | |

## Phase 3: Pipeline Integration

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `resolved_entities` to PipelineRecord | [ ] | |
| 3.2 | Update processing functions | [ ] | |
| 3.3 | Update Parquet schema | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files

| File | Action |
|------|--------|
| `src/nlp_policy_nz/kb/__init__.py` | Create |
| `src/nlp_policy_nz/kb/nz_entities.py` | Create |
| `src/nlp_policy_nz/kb/resolver.py` | Create |
| `src/nlp_policy_nz/kb/wikidata.py` | Create |
| `tests/test_kb.py` | Create |
