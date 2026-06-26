# Track 33: Graph, Vector, and Network Analysis

**Dependencies**: Tracks 17, 29, 31-32
**Parallelization Node**: Graph and Embedding Analytics
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Inventory graph artefacts: ontology mapping graph (Track 29), Wikidata KG (Track 17), NZ ontologies (Track 31), citation network, co-vote network, MP co-speech network | [ ] | conductor_orchestrator |
| 2 | Inventory vector artefacts: LanceDB embedding index, embedder model outputs, document/sentence/chunk vectors | [ ] | conductor_orchestrator |
| 3 | Record blockers for unavailable full graph/vector outputs | [ ] | conductor_orchestrator |
| 4 | Compute graph metrics: degree distribution, centrality (degree, betweenness, eigenvector), community detection (Louvain/Leiden), connected components | [ ] | conductor_orchestrator |
| 5 | Compute network metrics: MP voting bloc detection, bill co-sponsorship network, legislative topic citation network | [ ] | conductor_orchestrator |
| 6 | Compute vector metrics: cluster quality (silhouette score), dimensionality reduction (UMAP/PCA), nearest-neighbour distributions | [ ] | conductor_orchestrator |
| 7 | Compare graph neighbourhoods with vector similarity: do ontology-linked documents cluster in embedding space? | [ ] | conductor_orchestrator |
| 8 | Export artefacts: graph metrics JSON, vector cluster assignments, comparison tables, NetworkX/Mermaid/Plotly visualizations | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
