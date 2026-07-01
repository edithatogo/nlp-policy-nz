# Track 35 Visual Inspection Checklist

- Confirm SVG figures open in a browser or image viewer.
- Confirm Mermaid diagrams render in documentation tooling.
- Confirm CSV and LaTeX tables contain deterministic fixture-bounded values.
- Confirm blocked full-corpus outputs are not described as completed.

## Available artifacts

- [table] `tables/corpus_summary.csv`
- [table] `tables/corpus_summary.tex`
- [table] `tables/entity_density.csv`
- [table] `tables/ontology_coverage.csv`
- [table] `tables/topic_distribution.csv`
- [figure] `figures/embedding_projection.svg`
- [figure] `figures/entity_density.svg`
- [figure] `figures/network_overview.svg`
- [figure] `figures/temporal_trends.svg`
- [diagram] `diagrams/pipeline_architecture.mmd`
- [diagram] `diagrams/track_dependency.mmd`
- [diagram] `diagrams/workflow_data_flow.mmd`

## Blocked artifacts

- `full-corpus-embedding-umap`: Publication UMAP over the complete corpus requires canonical full-corpus vector exports; deterministic fixture projection is available as figures/embedding_projection.svg.
- `citation-graph-production`: Full citation graph figures require canonical citation edge exports. The checked-in network overview remains fixture-bounded.
