# Track 35: Analysis Artifact Execution and Figure Production

**Dependencies**: Tracks 32-34
**Parallelization Node**: Reproducible Artifact Production
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Define artefact manifest: tables (corpus summary, entity density, topic distribution, ontology coverage), figures (temporal trend plots, network visualizations, embedding UMAPs, citation graph), conceptual diagrams (pipeline architecture, ontology alignment), workflow diagrams (data flow, track dependency) | [x] | conductor_orchestrator |
| 2 | Link each artefact to its generating script or data source; mark artefacts requiring full-corpus or blocked data | [x] | conductor_orchestrator |
| 3 | Create `scripts/generate_all_artifacts.py` that orchestrates all available analysis pipelines and emits artefacts to `artifacts/` | [x] | conductor_orchestrator |
| 4 | Execute all available analysis pipelines on fixture/sample data; record skipped artefacts with blocker references | [x] | conductor_orchestrator |
| 5 | Generate tables: use corpus-statistics pipeline (Track 32) to produce CSV/LaTeX tables | [x] | conductor_orchestrator |
| 6 | Generate figures: use graph/vector analysis (Track 33) to produce PNG/SVG figures with publication-ready styling (colorblind-safe, journal font sizes) | [x] | conductor_orchestrator |
| 7 | Generate conceptual and workflow diagrams using Mermaid or scientific-schematics | [x] | conductor_orchestrator |
| 8 | Validate artefacts: schema conformance, file integrity, visual inspection checklist, LaTeX table compilability | [x] | conductor_orchestrator |

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.

## Implementation Note - 2026-07-01

Track 35 is implemented as deterministic artifact execution over the checked-in Track 32-34 outputs:

- `src/nlp_policy_nz/analysis/artifact_execution.py` builds an artifact bundle, manifest, tables, SVG figures, Mermaid diagrams, blocker records, and a visual inspection checklist.
- `scripts/generate_all_artifacts.py` and `nlp-policy-nz generate-analysis-artifacts` regenerate the `artifacts/` tree.
- `artifacts/` contains checked-in CSV/LaTeX tables, SVG figures, Mermaid diagrams, `analysis_artifact_manifest.json`, `analysis_artifact_blockers.json`, and `visual_inspection_checklist.md`.
- Full-corpus UMAP and citation graph production remain blocked until canonical corpus vectors and citation edge exports are supplied.
