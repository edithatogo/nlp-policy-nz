# Track 16 evidence

## Repo-side implementation

- `src/nlp_policy_nz/linked_data/foaf.py` provides FOAF graph generation and Turtle export for supplied MP profiles.
- `src/nlp_policy_nz/linked_data/sioc.py` provides Hansard speech-to-SIOC graph generation and Turtle export.
- `src/nlp_policy_nz/linked_data/rdf.py` provides shared namespace binding, sidecar path, serialization, and SPARQL query helpers.
- `src/nlp_policy_nz/cli/main.py` exposes `export-rdf` and `sparql` commands.
- `tests/test_linked_data.py` covers FOAF profile graph output, Turtle round-trip parsing, SIOC Hansard structure, RDF sidecar writing, SPARQL query results, and the CLI path.

## Review fixes

- Added the missing Conductor track index.
- Updated the specification from pending to repo-side complete.
- Kept the complete NZ MP current and historical coverage claim as an external data gate rather than overclaiming full knowledge-base coverage.

## Verification

- `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider -q tests\test_linked_data.py tests\test_ontology_coverage_audit.py tests\test_track25_ontology_coverage.py --basetemp C:\tmp\nlp-policy-nz-track16-review-pre` -> 15 passed.
- `.\.venv\Scripts\python.exe -m ruff check --no-cache src\nlp_policy_nz\linked_data tests\test_linked_data.py` -> passed.

## Residual external gate

- Full current and historical NZ MP FOAF profile coverage requires a complete upstream entity/Wikidata corpus and is not asserted by Track 16's fixture-backed exporter tests.
