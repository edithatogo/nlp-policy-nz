# Track 33: Graph, Vector, and Network Analysis

**Dependencies**: Tracks 17, 29, 31-32
**Parallelization Node**: Graph and Embedding Analytics
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Inventory graph artefacts: ontology mapping graph (Track 29), Wikidata KG (Track 17), NZ ontologies (Track 31), citation network, co-vote network, MP co-speech network | [x] | conductor_orchestrator |
| 2 | Inventory vector artefacts: LanceDB embedding index, embedder model outputs, document/sentence/chunk vectors | [x] | conductor_orchestrator |
| 3 | Record blockers for unavailable full graph/vector outputs | [x] | conductor_orchestrator |
| 4 | Compute graph metrics: degree distribution, centrality (degree, betweenness, eigenvector), community detection (Louvain/Leiden), connected components | [x] | conductor_orchestrator |
| 5 | Compute network metrics: MP voting bloc detection, bill co-sponsorship network, legislative topic citation network | [x] | conductor_orchestrator |
| 6 | Compute vector metrics: cluster quality (silhouette score), dimensionality reduction (UMAP/PCA), nearest-neighbour distributions | [x] | conductor_orchestrator |
| 7 | Compare graph neighbourhoods with vector similarity: do ontology-linked documents cluster in embedding space? | [x] | conductor_orchestrator |
| 8 | Export artefacts: graph metrics JSON, vector cluster assignments, comparison tables, NetworkX/Mermaid/Plotly visualizations | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.

## Implementation Note - 2026-07-01

Track 33 is implemented as a deterministic, fixture-bounded graph/vector/network
analysis layer:

- `src/nlp_policy_nz/analysis/graph_vector_network.py` builds a NetworkX graph
  from checked-in Track 29 ontology mappings, Track 31 NZ ontology candidates,
  Track 32 statistics availability, and deterministic vector fixtures.
- `data/analysis/` contains checked-in JSON, CSV, and Mermaid artifacts for
  graph metrics, vector metrics, graph/vector alignment, and blockers.
- `docs/graph_vector_network_analysis.md` records the publication-ready summary
  and explicit full graph/vector corpus blockers.
- `nlp-policy-nz graph-vector-analysis` exposes the writer for CI and
  reproducible local generation.
