# Track 36: Hugging Face Exploration Site

**Dependencies**: Tracks 8, 32-35
**Parallelization Node**: Public Exploration Interface
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define page structure: overview dashboard, corpus statistics explorer, ontology coverage matrix, graph/vector visualization page, dataset browser, publication protocol viewer | [ ] | conductor_orchestrator |
| 2 | Define fixture-mode behaviour (use `data/` fixture samples) and full-data-mode behaviour (load from LanceDB/Parquet) | [ ] | conductor_orchestrator |
| 3 | Create Hugging Face Space skeleton: Gradio or Streamlit app in `scripts/hf_space/` with `README.md`, `app.py`, `requirements.txt`, `packages.txt` | [ ] | conductor_orchestrator |
| 4 | Add corpus statistics explorer: load Track 32 outputs, display per-corpus metrics with Plotly charts | [ ] | conductor_orchestrator |
| 5 | Add ontology coverage page: render coverage matrix from Track 25 manifest, with expandable details per standard | [ ] | conductor_orchestrator |
| 6 | Add graph/vector visualization page: load Track 33 outputs, display NetworkX/Plotly interactive graphs and UMAP projections | [ ] | conductor_orchestrator |
| 7 | Add fixture-mode placeholder labels: for pages requiring full-corpus data, show "Requires full corpus - load via [link]" with sample fixture fallback | [ ] | conductor_orchestrator |
| 8 | Add deployment docs, smoke tests (does app load?), and CI check for Space build | [ ] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
