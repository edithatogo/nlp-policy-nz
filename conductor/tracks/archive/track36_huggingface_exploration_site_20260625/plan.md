# Track 36: Hugging Face Exploration Site

**Dependencies**: Tracks 8, 32-35
**Parallelization Node**: Public Exploration Interface
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define page structure: overview dashboard, corpus statistics explorer, ontology coverage matrix, graph/vector visualization page, dataset browser, publication protocol viewer | [x] | conductor_orchestrator |
| 2 | Define fixture-mode behaviour (use `data/` fixture samples) and full-data-mode behaviour (load from LanceDB/Parquet) | [x] | conductor_orchestrator |
| 3 | Extend the repo-standard Hugging Face Space skeleton in `spaces/` with README, app, and requirements updates | [x] | conductor_orchestrator |
| 4 | Add corpus statistics explorer: load Track 32 outputs, display per-corpus metrics with Plotly charts | [x] | conductor_orchestrator |
| 5 | Add ontology coverage page: render coverage matrix from Track 25/29-31 summaries, with details per track | [x] | conductor_orchestrator |
| 6 | Add graph/vector visualization page: load Track 33 outputs, display Plotly projection and checked-in Mermaid network | [x] | conductor_orchestrator |
| 7 | Add fixture-mode placeholder labels: for pages requiring full-corpus data, show "Requires full corpus" with sample fixture fallback | [x] | conductor_orchestrator |
| 8 | Add deployment docs, smoke tests (does app load?), and CI-compatible Space checks | [x] | conductor_orchestrator |

## Implementation Note

The generated plan originally named `scripts/hf_space/`, but this repository already uses `spaces/` as the Hugging Face Space source directory and the deployment tooling uploads that path. Track 36 therefore extends `spaces/app.py`, `spaces/README.md`, and `spaces/requirements.txt` instead of adding a competing Space scaffold.

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
