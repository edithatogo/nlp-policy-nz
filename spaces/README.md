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

- **Search** — Full-text search over document chunks
- **Citations** — NZ Act cross-reference frequency analysis
- **Te Reo Maori** — Term frequency visualisation
- **Stats** — Corpus-level metrics dashboard

## Usage

Upload a Parquet file produced by the `nlp-policy-nz` pipeline, then explore the tabs.

```bash
# Process a dataset first
nlp-policy-nz process -i data/acts/ -o output/legislation.parquet -s legislation

# Then launch locally
python spaces/app.py
```
