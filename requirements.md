# Requirements: nlp-policy-nz

## Runtime Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | >=3.13 | Core runtime (PEP 703 free-threaded compatible) |
| pixi | latest | Multi-language environment orchestration |

## Core Dependencies

### NLP & ML Engine

| Package | Version | Purpose |
|---------|---------|---------|
| spaCy | >=3.7.0 | Syntactic parsing, tokenization, EntityRuler |
| transformers | >=4.40.0 | Hugging Face transformer models |
| torch | >=2.2.0 | PyTorch backend for transformers |
| bitsandbytes | >=0.42.0 | 4-bit/8-bit quantization for local LLM loading |
| datasets | >=2.19.0 | Hugging Face dataset loading/uploading |
| huggingface_hub | >=0.23.0 | Hugging Face Hub API client |

### Data Processing & Storage

| Package | Version | Purpose |
|---------|---------|---------|
| polars | >=1.0.0 | Rust-backed DataFrame operations |
| pyarrow | >=16.0.0 | Apache Arrow/Parquet serialization |
| narwhals | >=1.0.0 | DataFrame-agnostic compatibility layer |
| lancedb | >=0.6.0 | Serverless vector database (Rust/Arrow-native) |
| faiss-cpu | >=1.8.0 | In-memory similarity search |
| networkx | >=3.0 | Relational graphing (debates ↔ legislation) |
| msgspec | >=0.18.0 | High-performance struct validation & serialization |

### Web & API

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | >=0.110.0 | Inference API server |
| uvicorn | >=0.27.0 | ASGI server for FastAPI |
| gradio | >=4.0.0 | Interactive visualization Spaces |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| requests | >=2.31.0 | HTTP client (Zenodo API) |
| lingua-language-detector | (via pip) | Language detection (Te Reo Māori / English) |

## Development Dependencies

### Testing

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.0 | Test runner |
| hypothesis | >=6.90 | Property-based testing |
| mutatest | >=3.0 | Mutation testing |

### Linting & Quality

| Package | Version | Purpose |
|---------|---------|---------|
| ruff | >=0.3.0 | Linting, formatting, import sorting |
| tach | >=0.5.0 | Module boundary enforcement |
| import-linter | >=2.0 | Architectural boundary enforcement |
| complexipy | >=0.2.0 | Cognitive complexity analysis |
| vale | >=3.0 | Prose linting (docs) |

### CI/CD & GitOps

| Tool | Purpose |
|------|---------|
| pre-commit | Git hook automation |
| GitHub Actions | CI/CD orchestration |
| maturin | Rust/PyO3 extension builds |

## Infrastructural Requirements (Future)

| Component | Status | Purpose |
|-----------|--------|---------|
| OpenTelemetry | Planned | Distributed tracing & metrics |
| Scalene / Memray | Planned | CPU/memory profiling |
| Northflank | Planned | Preview environment deployment |
| Argo CD | Planned | GitOps production deployment |
| Astro | Planned | Documentation portal |
