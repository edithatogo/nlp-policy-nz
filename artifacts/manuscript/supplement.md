# Supplement

## Ontology coverage matrix

See `artifacts/tables/ontology_coverage.csv` and the Track 36 Space coverage table for the current fixture-bounded matrix.

## Mapping examples

Mapping evidence is sourced from Track 29-31 ontology artifacts and summarized in the Track 34 publication protocol claims.

## Corpus statistics detail tables

Detailed corpus tables are available under `data/statistics/` and publication-ready summaries under `artifacts/tables/`.

## Figure gallery

- `artifacts/figures/temporal_trends.svg`
- `artifacts/figures/entity_density.svg`
- `artifacts/figures/network_overview.svg`
- `artifacts/figures/embedding_projection.svg`

## Reproducibility instructions

1. `nlp-policy-nz publication-protocol --output-dir data/publication`
2. `nlp-policy-nz generate-analysis-artifacts --output-dir artifacts`
3. `nlp-policy-nz generate-manuscript-package --output-dir artifacts/manuscript`
4. `pixi run python -m pytest -q tests/test_track37_manuscript_review.py`

## Operational notes

The repository is intended to be executed from GitHub Actions for routine validation, but the same deterministic artifacts can be consumed locally or by downstream workflows. Paper text should distinguish between repository-run jobs, library-style integration, CLI automation, and exported datasets so the operating model is unambiguous.

## Evidence boundary

The package is generated from checked-in Track 34-36 artifacts. Full-corpus claims, live external reviewer agents, and actual arXiv submission remain blocked until canonical exports and credentials are supplied.
