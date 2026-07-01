# Track 17 evidence

## Repo-side implementation

- `data/ontologies/nz_wikidata_map.ttl` maps NZ Acts, MPs, political parties, electorates, and courts to Wikidata classes in OWL/Turtle.
- `src/nlp_policy_nz/kb/wikidata_kg.py` provides the Wikidata SPARQL client, cached bulk resolver, property enrichment, federated query helper, JSON-LD export, and JSON entity loader.
- `src/nlp_policy_nz/kb/sparql_cache.py` provides the persistent JSON cache used by the resolver.
- `data/ontologies/wikidata_federated_example.rq` records the federated SPARQL example.
- `src/nlp_policy_nz/cli/main.py` exposes the `knowledge-graph` JSON-LD export command.
- `tests/test_wikidata_kg.py` covers ontology loading, resolver caching, mocked SPARQL client behavior, enrichment, JSON-LD export, federated query stability, CLI export, and input validation.

## Review fixes

- Added the missing Conductor track index.
- Updated the specification from pending to repo-side complete.
- Kept measured >90% resolver precision as an external evaluation gate rather than overclaiming live Wikidata precision from deterministic fake-client tests.

## Verification

- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_wikidata_kg.py tests\test_kb.py tests\test_ontology_coverage_audit.py tests\test_track25_ontology_coverage.py --basetemp C:\tmp\nlp-policy-nz-track17-review-pre` -> 31 passed, 1 rdflib deprecation warning.
- `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\kb tests\test_wikidata_kg.py tests\test_kb.py` -> passed.

## Residual external gate

- Measured >90% bulk QID resolver precision requires a curated NZ legal/parliamentary entity benchmark and live or snapshotted Wikidata reconciliation evidence.
