# Track 7 Evidence - Downstream API and PolicyGraph

Track 7 is complete for repo-side downstream API and relational graph scaffolding.

Implemented surfaces:

- `src/nlp_policy_nz/api/__init__.py` exposes `process_legislation`, `process_hansard`, and `search_similar` wrappers backed by `pipeline_api.py`.
- `src/nlp_policy_nz/pipeline_api.py` implements legislation/Hansard processing and LanceDB-backed search helpers.
- `src/nlp_policy_nz/cli/main.py` exposes `process` and `search` subcommands for downstream command-line use.
- `src/nlp_policy_nz/cli/graph.py` provides `PolicyGraph`, typed node labels, citation/reference edges, graph queries, rankings, and JSON serialization.

Validation evidence:

- `tests/test_cli.py` covers parser and CLI command behavior for the public command surface.
- `tests/test_graph.py` covers `PolicyGraph` node/edge creation, citation and section-reference edges, missing-node behavior, rankings, and JSON round trips.
- `tests/test_ontology_and_pipeline_helpers.py` covers pipeline API search-helper behavior with mocked LanceDB adapters.
- The Track 7 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Production HTTP API maturity, authentication, rate limiting, and observability belong to later production-hardening tracks.
- Full cross-repo consumer validation remains external to this repo-side archive step.
