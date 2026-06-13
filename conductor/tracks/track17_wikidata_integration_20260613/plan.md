# Track 17: Wikidata NZ Ontology Integration

**Dependencies**: Track 12
**Parallelization Node**: Knowledge Graph
**Status**: Pending

---

## Phase 1: Ontology Mapping

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Research Wikidata coverage of NZ entities | [ ] | |
| 1.2 | Create OWL ontology map `data/ontologies/nz_wikidata_map.ttl` | [ ] | |
| 1.3 | Document entity-to-QID mappings | [ ] | |
| 1.4 | Write ontology validity tests | [ ] | |

## Phase 2: QID Resolution

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Implement SPARQL bulk QID resolver with cache | [ ] | |
| 2.2 | Implement property enrichment from Wikidata | [ ] | |
| 2.3 | Integrate into entity resolution pipeline | [ ] | |
| 2.4 | Write SPARQL query tests | [ ] | |

## Phase 3: Knowledge Graph Export

**Status**: Pending

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Implement JSON-LD knowledge graph exporter | [ ] | |
| 3.2 | Create federated SPARQL query examples | [ ] | |
| 3.3 | Add `knowledge-graph` CLI subcommand | [ ] | |
| 3.4 | Run full test suite | [ ] | |

## Files

| File | Action |
|------|--------|
| `data/ontologies/nz_wikidata_map.ttl` | Create |
| `src/nlp_policy_nz/kb/wikidata_kg.py` | Create |
| `src/nlp_policy_nz/kb/sparql_cache.py` | Create |
| `tests/test_wikidata_kg.py` | Create |
