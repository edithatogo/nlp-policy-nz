# Track 12: Named Entity Resolution & Wikidata Linking

**Dependencies**: Track 5
**Parallelization Node**: Knowledge Base Integration
**Status**: Archived

---

## Phase 1: Knowledge Base Construction

**Status**: Archived

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Create `src/nlp_policy_nz/kb/` module with entity schema | [x] | |
| 1.2 | Compile KB entries for MPs, parties, electorates, ministries, courts | [x] | |
| 1.3 | Include Wikidata QIDs for each entry | [x] | |
| 1.4 | Write KB loading and query tests | [x] | |

## Phase 2: Entity Resolution

**Status**: Archived

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Implement `EntityResolver` with fuzzy matching | [x] | |
| 2.2 | Add context disambiguation (party, date range) | [x] | |
| 2.3 | Implement Wikidata SPARQL enrichment | [x] | |
| 2.4 | Write resolution accuracy tests | [x] | |

## Phase 3: Pipeline Integration

**Status**: Archived

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `resolved_entities` to PipelineRecord | [x] | |
| 3.2 | Update processing functions | [x] | |
| 3.3 | Update Parquet schema | [x] | |
| 3.4 | Run full test suite | [x] | |

## Files

| File | Action |
|------|--------|
| `data/kb/nz_entities.json` | Create |
| `scripts/build_nz_entity_kb.py` | Create |
| `src/nlp_policy_nz/kb/__init__.py` | Create/update |
| `src/nlp_policy_nz/kb/nz_entities.py` | Create/update |
| `src/nlp_policy_nz/kb/resolver.py` | Create/update |
| `src/nlp_policy_nz/kb/wikidata.py` | Create |
| `src/nlp_policy_nz/pipeline_api.py` | Update |
| `src/nlp_policy_nz/storage/serialization.py` | Update |
| `tests/fixtures/kb_resolution_benchmark.json` | Create |
| `tests/test_kb.py` | Create/update |

## Implementation Note - 2026-06-22

Track 12 entity linking is implemented repo-side:

- Added a generated Wikidata-backed KB snapshot with 2,124 records: 1,503 MPs, 186 parties, 360 electorates, 66 ministries, and 9 courts.
- Added `EntityRecord`, `EntityContext`, JSON KB loading, and deterministic fallback seed records.
- Added fuzzy alias matching, date/party/electorate context scoring, overlap deduplication, and schema-safe resolved entity dictionaries.
- Added a registered `nz_entity_resolver` spaCy component that links `doc.ents` and supplements with exact KB alias matches.
- Wired legislation and Hansard processing through the spaCy resolver component with inferred party/electorate context and Hansard filename date context.
- Added cached Wikidata property enrichment via the existing SPARQL client/cache layer.
- Added `resolved_entities` to `PipelineRecord`, DataFrame/Parquet serialization, and processing paths.
- Expanded the labelled benchmark to 14 MP/party/electorate/ministry/court cases and changed precision evaluation so unresolved cases count against the threshold.

Verification:

- `ruff check src\nlp_policy_nz\kb tests\test_kb.py scripts\build_nz_entity_kb.py src\nlp_policy_nz\pipeline_api.py` passed; Ruff cache writes were denied but checks passed.
- `pytest tests\test_kb.py -p no:cacheprovider -q` passed: 13 passed.
- `pytest tests\test_storage.py tests\test_wikidata_kg.py -p no:cacheprovider -q` passed: 25 passed, 1 rdflib deprecation warning.
- `coverage report --data-file=.tmp\coverage\track12-fixes.coverage --include=src\nlp_policy_nz\kb\nz_entities.py,src\nlp_policy_nz\kb\resolver.py,src\nlp_policy_nz\kb\wikidata.py -m` reported 95% total coverage.

Residual note: the full repository suite was not run because the worktree contains many unrelated in-progress tracks; focused Track 12 and compatibility gates passed.

## Archive Note - 2026-06-22

Archived after focused Track 12 verification passed: `pytest tests\test_kb.py -p no:cacheprovider -q` reported 13 passed.
