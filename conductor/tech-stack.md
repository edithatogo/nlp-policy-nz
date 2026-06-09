# Technology Stack: nlp-policy-nz

This document defines the bleeding-edge, high-performance technology stack for the `nlp-policy-nz` shared core engine and its continuous delivery workflow.

---

## 1. Runtime & Execution Environment

- **Python Version**: Python `3.14t` (Free-Threaded / No-GIL mode, conforming to **PEP 703**). This enables true multi-threaded CPU processing for parallel text cleaning and tokenization.
- **Inline Script Metadata**: Adhere to **PEP 723** for single-file scripts (e.g., pipeline scripts, data seeding scripts), specifying dependencies inline for self-contained execution.

---

## 2. Dependency Management & Build Tooling

- **Environment & Package Management**: `pixi` (for multi-language, cross-platform environment orchestration and C/Rust toolchain dependencies) integrated with `uv` (for ultra-fast Python package resolution and virtual environment management).
- **Build System**: `hatchling` as the PEP 517 build backend, combined with `uv build` for packaging compilation.
- **Rust Integration**: `maturin` and `pyo3` for compiling and building custom Rust extensions directly into the Python package.

---

## 3. High-Performance Validation & Dataframe Portability

- **Data Validation & Struct Parsing**: `msgspec` (SOTA, compiled Cython/C library for lightning-fast struct validation and serialization, significantly outperforming Pydantic for high-throughput pipelines).
- **DataFrame Portability**: `narwhals` (lightweight compatibility layer enabling zero-copy, dataframe-agnostic code execution across Polars, PyArrow, and Pandas).

---

## 4. NLP & Machine Learning Engine

- **Syntactic Parser**: `spaCy` v3.7+ (utilizing custom tokenizers and `EntityRuler`).
- **Semantic Layer**: Hugging Face `transformers` (configured with Rust-backed fast tokenizers `use_fast=True`), `torch`, and `spacy-transformers` / `spacy-alignments` (Rust-backed alignment layer).
- **Quantization**: `bitsandbytes` (4-bit quantization for local loading of `Equall/SaulLM-7B`).
- **Language Detection**: `lingua-rs` (via Python bindings, providing SOTA language detection for short policy segments).
- **Data Engine**: `polars` (Rust-backed DataFrame library for lightning-fast Parquet operations).
- **Polars Plugins (Rust-Native Expressions)**: Custom compiled Rust functions registered directly with Polars. These must be structured as a decoupled, isolated crate so they can be easily contributed to the upstream Polars plugins ecosystem.

---

## 5. Local Vector Database & Graphing

- **Local Vector Database**: `lancedb` (serverless, open-source vector database written in Rust, built on top of Apache Arrow for zero-copy queries directly from Polars DataFrames).
- **Relational Graphing**: `networkx` (in-memory relational graphs).

---

## 6. Testing, Linting & Code Quality (Strict Configuration)

- **Linting, Formatting, and Imports**: `ruff` (enforced for ALL linting, formatting, import sorting, and code upgrades, configured with strict settings activated early).
- **Modular Containment**: 
  - `Tach` (for strict module boundary containment and dependency visualization).
  - `import-linter` (enforcing clean architectural boundaries).
- **Complexity Guard**: `Complexipy` (cognitive complexity analyzer).
- **Prose Linting**: `vale` (for documentation spelling, grammar, and style guidelines).
- **Testing Suite**:
  - `pytest` (core test runner).
  - `Hypothesis` (property-based testing for robust edge-case validation).
  - `Mutatest` (mutation testing to verify test assertion quality).
- **Observability Testing**: `Tracetest` with native OpenTelemetry instrumentation for distributed trace-based testing.

---

## 7. Observability, Profiling & Performance Analysis

- **Telemetry**: OpenTelemetry Python SDK for native logging, metrics, and trace export.
- **Profiling Suite**:
  - `scalene` (CPU, GPU, and memory profiler with AI-powered optimization advice).
  - `memray` (detailed memory profiling to trace leaks in large-scale dataset loads).
  - `py-spy` & `austin` (sampling profilers for zero-overhead performance debugging in production/development threads).

---

## 8. Deployment & GitOps Orchestration

- **Pipeline Orchestrator**: GitHub Actions.
- **The Preview Engine**: **Northflank** (automatically spins up preview environments for pull requests).
- **Production GitOps Deployer**: **Argo CD** (enforces GitOps-based declarative deployment to production clusters).

---

## 9. Documentation Setup

- **Documentation Portal**: **Astro** (modern static site generator built for speed, deployed on GitHub Pages).
