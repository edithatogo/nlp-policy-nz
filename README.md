# nlp-policy-nz

**SOTA shared core NLP pipeline for New Zealand legislation and Hansard corpora.**

A modular, high-performance NLP preprocessing pipeline purpose-built for Aotearoa New Zealand's legislative and parliamentary texts. The pipeline integrates Māori Language validation, syntactic parsing, semantic analysis, and efficient vector storage into a unified Rust-accelerated Python package.

## Features

- **Māori Language Guard** — Validate and enforce correct Māori orthographic conventions in legislative and parliamentary texts.
- **Syntactic Layer** — Dependency parsing, constituency parsing, and POS tagging using spaCy and transformer models.
- **Semantic Layer** — Entity recognition, relation extraction, and embedding-based semantic search.
- **Storage Backends** — High-performance vector and document storage via LanceDB, FAISS, and Polars.
- **CLI Interface** — Batch processing, interactive queries, and pipeline configuration.
- **Hugging Face Hub** — Push processed Parquet datasets to Hugging Face Hub with auto-generated dataset cards.
- **Interactive Visualization Space** — Gradio-based Space with full-text search, citation network explorer, Te Reo Māori term visualisation, and corpus statistics dashboard.

## Requirements

- Python 3.13+
- Rust toolchain (for maturin builds)

## Installation

```bash
pip install nlp-policy-nz
```

## Usage

```bash
# Process legislation through the NLP pipeline
nlp-policy-nz process -i data/acts/ -o output/legislation.parquet -s legislation

# Search the vector index
nlp-policy-nz search -q "climate change adaptation" -k 5 -d ./lancedb_data

# Upload a processed dataset to Hugging Face Hub
nlp-policy-nz upload-dataset --parquet output/legislation.parquet --repo-id user/nz-legislation

# Deploy the interactive Gradio Space to Hugging Face Hub
nlp-policy-nz deploy-space --repo-id user/nz-policy-explorer

# Launch the Gradio Space locally
python spaces/app.py

# Export one source section as offline rules-as-code bridge JSON-LD
nlp-policy-nz rac-export \
    --input data/sections/example-section.txt \
    --output output/rac/example-section.json \
    --citation-path nz/statutes/example-act/2026/10 \
    --source-url https://legislation.govt.nz/example-act/section/10 \
    --retrieved-at 2026-06-29T00:00:00Z
```

## Documentation

- [Axiom Foundation relevance](docs/axiom-foundation-relevance.md) records the selective source identity, provenance, RuleSpec bridge, and bill/Hansard linkage conventions borrowed from Axiom Foundation repositories.
- [Build notes](docs/build_backend.md) describe the current packaging decisions.
- [Pipeline record serialization](docs/pydantic_vs_msgspec.md) records the serialization benchmark decision.

## 🏛️ Archiving & Releases

Processed corpora can be archived to [Zenodo](https://zenodo.org) for citable, long-term preservation.

### CLI Commands

```bash
# Archive a single Parquet file to Zenodo Sandbox (testing)
nlp-policy-nz archive-to-zenodo \
    --parquet output/legislation.parquet \
    --title "NZ Legislation Corpus" \
    --description "NLP preprocessed NZ legislation" \
    --creators '[{"name": "Doe, Jane"}]'

# Create a versioned release archive and publish to Zenodo
nlp-policy-nz release \
    --parquet output/legislation.parquet \
    --version 1.0.0 \
    --title "NZ Legislation v1.0.0" \
    --description "NLP preprocessed NZ legislation corpus" \
    --creators '[{"name": "Doe, Jane"}]
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `ZENODO_SANDBOX_TOKEN` | API token for [Zenodo Sandbox](https://sandbox.zenodo.org) |
| `ZENODO_PRODUCTION_TOKEN` | API token for [Zenodo Production](https://zenodo.org) |

### Shell Script

For one-shot local releases without the CLI, use the convenience script:

```bash
bash scripts/release.sh --parquet output/legislation.parquet --version 1.0.0 --title "..." --description "..." --creators '...'
bash scripts/release.sh --parquet output/legislation.parquet --version 1.0.0 --title "..." --description "..." --creators '...' --dry-run
```

### GitHub Actions

On tag push (e.g. `v1.0.0`), the [Release workflow](.github/workflows/release.yml) automatically creates a release archive, uploads it to Zenodo, and creates a GitHub Release.

## License

MIT
