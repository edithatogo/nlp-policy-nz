# Track 33 Evidence: Graph, Vector, and Network Analysis

## Repo-Side Implementation

- Added `src/nlp_policy_nz/analysis/graph_vector_network.py` for deterministic Track 33 graph, vector, network, and alignment analysis.
- Added `nlp-policy-nz graph-vector-analysis` to export artifacts from checked-in ontology/statistics inputs and deterministic vector fixtures.
- Added checked-in artifacts under `data/analysis/`: `graph_vector_manifest.json`, `graph_vector_graph_metrics.json`, `graph_vector_vector_metrics.json`, `graph_vector_alignment.csv`, `graph_vector_blockers.json`, and `graph_vector_network.mmd`.
- Added `docs/graph_vector_network_analysis.md` as the publication-ready summary.
- Added `tests/test_track33_graph_vector_network.py` and `tests/test_track33_conductor.py`.

## Boundaries

- Checked-in statistics are fixture-bounded and do not claim canonical full graph/vector coverage.
- True graph metrics over citation, co-vote, co-speech, and Wikidata networks require full graph exports.
- True vector-space metrics require a canonical full LanceDB or PipelineRecord vector export.
- Missing full graph/vector inputs are recorded in `graph_vector_blockers.json`.

## Closeout Validation

- `pixi run python -m pytest -q tests\test_track33_graph_vector_network.py tests\test_track33_conductor.py tests\test_cli.py tests\test_track29_mapping_graph.py tests\test_track31_nz_ontologies.py tests\test_track32_corpus_statistics.py tests\test_track32_conductor.py` passed.
- `pixi run python -m ruff check --no-cache src\nlp_policy_nz\analysis\graph_vector_network.py src\nlp_policy_nz\analysis\__init__.py src\nlp_policy_nz\__init__.py src\nlp_policy_nz\cli\main.py tests\test_track33_graph_vector_network.py tests\test_track33_conductor.py tests\test_cli.py` passed.
- `git diff --check` passed.
