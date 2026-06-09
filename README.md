# nlp-policy-nz

**SOTA shared core NLP pipeline for New Zealand legislation and Hansard corpora.**

A modular, high-performance NLP preprocessing pipeline purpose-built for Aotearoa New Zealand's legislative and parliamentary texts. The pipeline integrates Māori Language validation, syntactic parsing, semantic analysis, and efficient vector storage into a unified Rust-accelerated Python package.

## Features

- **Māori Language Guard** — Validate and enforce correct Māori orthographic conventions in legislative and parliamentary texts.
- **Syntactic Layer** — Dependency parsing, constituency parsing, and POS tagging using spaCy and transformer models.
- **Semantic Layer** — Entity recognition, relation extraction, and embedding-based semantic search.
- **Storage Backends** — High-performance vector and document storage via LanceDB, FAISS, and Polars.
- **CLI Interface** — Batch processing, interactive queries, and pipeline configuration.

## Requirements

- Python 3.13+
- Rust toolchain (for maturin builds)

## Installation

```bash
pip install nlp-policy-nz
```

## License

MIT
