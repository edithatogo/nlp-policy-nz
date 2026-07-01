# Track 35 Evidence

## Generated Artifacts

- `artifacts/analysis_artifact_manifest.json`
- `artifacts/analysis_artifact_blockers.json`
- `artifacts/visual_inspection_checklist.md`
- `artifacts/tables/corpus_summary.csv`
- `artifacts/tables/corpus_summary.tex`
- `artifacts/tables/entity_density.csv`
- `artifacts/tables/topic_distribution.csv`
- `artifacts/tables/ontology_coverage.csv`
- `artifacts/figures/temporal_trends.svg`
- `artifacts/figures/entity_density.svg`
- `artifacts/figures/network_overview.svg`
- `artifacts/figures/embedding_projection.svg`
- `artifacts/diagrams/pipeline_architecture.mmd`
- `artifacts/diagrams/workflow_data_flow.mmd`
- `artifacts/diagrams/track_dependency.mmd`

## Source Inputs

- Track 32 checked-in statistics under `data/statistics/`.
- Track 33 checked-in graph/vector outputs under `data/analysis/`.
- Track 34 checked-in publication protocol under `data/publication/` and `docs/publication_protocol.md`.

## Validation

- `pixi run python -m pytest -q tests\test_track35_analysis_artifacts.py tests\test_cli.py -q`
- `pixi run python -m ruff check --no-cache src\nlp_policy_nz\analysis\artifact_execution.py src\nlp_policy_nz\analysis\__init__.py src\nlp_policy_nz\cli\main.py src\nlp_policy_nz\__init__.py tests\test_track35_analysis_artifacts.py tests\test_cli.py scripts\generate_all_artifacts.py`

## Blocker Boundary

Full-corpus UMAP and full citation graph production remain blocked until canonical full-corpus vector exports and citation edge exports are supplied. Fixture-bounded SVGs and Mermaid diagrams are available for repo-side publication scaffolding.
