---
title: nlp-policy-nz Explorer
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
license: mit
tags:
  - nlp
  - new-zealand
  - legislation
  - parliament
  - visualization
---

# nlp-policy-nz Explorer

Interactive visualisation of New Zealand parliamentary and legislative NLP datasets produced by the `nlp-policy-nz` pipeline.

## Features

- **Overview** - Bounded Track 32-35 artifact summary with explicit fixture/full-corpus labels
- **Corpus Statistics** - Track 32 per-corpus, per-year, and entity metrics with Plotly charts
- **Ontology Coverage** - Track 25/29-31 coverage and mapping summaries
- **Graph and Vectors** - Track 33 graph metrics, vector projection, alignment table, and Mermaid network
- **Artifacts** - Track 35 generated publication tables, figures, diagrams, and inspection checklist
- **Publication Protocol** - Track 34 evidence-mapped publication claims and overclaim review
- **Dataset Browser** - Optional uploaded Parquet search, citation, Te Reo Maori, and corpus statistics tools

## Usage

The Space starts in fixture mode and loads checked-in artifacts from `data/`, `docs/`, and `artifacts/`. This mode is deterministic and works without Hugging Face, Zenodo, LanceDB, or external API credentials.

Upload a Parquet file produced by the `nlp-policy-nz` pipeline in the Dataset Browser tab for local full-data exploration. Corpus-wide claims still require supplied canonical full-corpus Parquet or LanceDB exports.

```bash
# Process a dataset first
nlp-policy-nz process -i data/acts/ -o output/legislation.parquet -s legislation

# Then launch locally
python spaces/app.py

# CI-friendly smoke tests
python -m pytest -q tests/test_gradio_space.py
```
