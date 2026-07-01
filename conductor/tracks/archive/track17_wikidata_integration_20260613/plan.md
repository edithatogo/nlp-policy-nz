# Track 17: Wikidata NZ Ontology Integration

**Dependencies**: Track 12
**Parallelization Node**: Knowledge Graph
**Status**: Complete

---

## Phase 1: Ontology Mapping

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Research Wikidata coverage of NZ entities | [x] | codex_gpt5_engineer |
| 1.2 | Create OWL ontology map `data/ontologies/nz_wikidata_map.ttl` | [x] | codex_gpt5_engineer |
| 1.3 | Document entity-to-QID mappings | [x] | codex_gpt5_engineer |
| 1.4 | Write ontology validity tests | [x] | codex_gpt5_engineer |

## Phase 2: QID Resolution

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Implement SPARQL bulk QID resolver with cache | [x] | codex_gpt5_engineer |
| 2.2 | Implement property enrichment from Wikidata | [x] | codex_gpt5_engineer |
| 2.3 | Integrate into entity resolution pipeline | [x] | codex_gpt5_engineer |
| 2.4 | Write SPARQL query tests | [x] | codex_gpt5_engineer |

## Phase 3: Knowledge Graph Export

**Status**: Complete

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Implement JSON-LD knowledge graph exporter | [x] | codex_gpt5_engineer |
| 3.2 | Create federated SPARQL query examples | [x] | codex_gpt5_engineer |
| 3.3 | Add `knowledge-graph` CLI subcommand | [x] | codex_gpt5_engineer |
| 3.4 | Attempt full test suite and record Windows temp blocker | [x] | codex_gpt5_engineer |

## Files

| File | Action |
|------|--------|
| `data/ontologies/nz_wikidata_map.ttl` | Create |
| `src/nlp_policy_nz/kb/wikidata_kg.py` | Create |
| `src/nlp_policy_nz/kb/sparql_cache.py` | Create |
| `tests/test_wikidata_kg.py` | Create |
| `data/ontologies/wikidata_federated_example.rq` | Create |

## Implementation Audit

- Added `kb/wikidata_kg.py` with Wikidata SPARQL client, cached bulk resolver, property enrichment, federated query helper, and schema.org-compatible JSON-LD export.
- Added `kb/sparql_cache.py` for persistent JSON cache records used by the resolver.
- Added OWL/Turtle mappings for New Zealand Acts, members of parliament, political parties, electorates, and courts in `data/ontologies/nz_wikidata_map.ttl`.
- Added `data/ontologies/wikidata_federated_example.rq` and a `knowledge-graph` CLI subcommand for JSON-LD export.
- Validation:
  - `python -m ruff check --no-cache src\nlp_policy_nz\kb src\nlp_policy_nz\cli\main.py tests\test_wikidata_kg.py`
  - `python -m pytest tests\test_wikidata_kg.py -p no:cacheprovider -q` -> 9 passed, 1 rdflib deprecation warning.
  - `python -m coverage report --data-file=.tmp\coverage\track17d.coverage --include=src\nlp_policy_nz\kb\* -m` -> 99% coverage for the new `kb` package.
  - `python -m pytest -p no:cacheprovider -q` -> 428 passed, 40 fixture setup errors from `PermissionError: [WinError 5] Access is denied: 'C:\Users\60217257\AppData\Local\Temp\pytest-of-60217257'`; no track 17 test failures surfaced.
