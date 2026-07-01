# Track 33: Graph, Vector, and Network Analysis

- [Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Metadata](./metadata.json)
- [Evidence](./evidence.md)

## Implementation

- `src/nlp_policy_nz/analysis/graph_vector_network.py`
- `src/nlp_policy_nz/cli/main.py` (`graph-vector-analysis`)
- `tests/test_track33_graph_vector_network.py`
- `tests/test_track33_conductor.py`

## Outputs

- `data/analysis/graph_vector_manifest.json`
- `data/analysis/graph_vector_graph_metrics.json`
- `data/analysis/graph_vector_vector_metrics.json`
- `data/analysis/graph_vector_alignment.csv`
- `data/analysis/graph_vector_blockers.json`
- `data/analysis/graph_vector_network.mmd`
- `docs/graph_vector_network_analysis.md`

## Boundary

The checked-in outputs are deterministic, fixture-bounded Track 33 artifacts. Full graph/vector publication requires supplied full-corpus graph exports and vector indexes.
