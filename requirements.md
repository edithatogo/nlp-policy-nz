# Requirements: nlp-policy-nz — MoSCoW Prioritisation

> **MoSCoW**: Must Have · Should Have · Could Have · Won't Have (this phase)

---

## Phase I (Tracks 1-9) — DELIVERED ✅

All Phase I requirements are **Must Have** and are complete.

## Phase II (Tracks 10-23) — MoSCoW

### 🔴 M — Must Have (required for legal viability)

| ID | Requirement | Track(s) | Dep |
|----|-------------|----------|-----|
| M1 | Deontic Modality Detection ("must/shall/may/must not") | T10 | T4,T5 |
| M2 | Named Entity Resolution (MPs, parties, electorates → Wikidata) | T12 | T5 |
| M3 | Smoke/Integration/E2E Tests (complete testing pyramid) | T23 | T1 |
| M4 | Ruff Max Strict (ANN, D, TCH, YTT, RET across all source) | T23 | T1 |
| M5 | pyright Strict Typing (`ty` module convention across all source) | T23 | T1 |
| M6 | Codecov + Coverage Gate (branch coverage in CI) | T23 | T1 |

### 🟡 S — Should Have (important, not blocking)

| ID | Requirement | Track(s) | Dep |
|----|-------------|----------|-----|
| S1 | Temporal Expression Extraction (dates, deadlines, periods) | T11 | T4,T5 |
| S2 | Argument Mining & Stance (pro/con/neutral in Hansard) | T13 | T5,T7 |
| S3 | AU→NZ Domain Transfer (fine-tune Open Australian Legal LLM) | T20,T22 | T5,T6 |
| S4 | MLEB-NZ Benchmark (extend MLEB with 7th jurisdiction) | T22 | T12 |
| S5 | OpenTelemetry Tracing (spans across all components) | T19 | T1,T6 |
| S6 | Scalene/Memray Profiling (baseline benchmarks) | T19,T23 | T1 |

### 🔵 C — Could Have (valuable enhancements)

| ID | Requirement | Track(s) | Dep |
|----|-------------|----------|-----|
| C1 | Akoma-Ntoso v3 Compliance (FRBR, TLCEvent, all doc types) | T14 | T4 |
| C2 | PROV-O Provenance (sidecar `.prov.json` per run) | T15 | T6,T9 |
| C3 | FOAF/SIOC Discourse Export (RDF/Turtle linked data) | T16 | T7,T12 |
| C4 | Wikidata Knowledge Graph (OWL mapping + SPARQL) | T17 | T12 |
| C5 | Voting Record Analysis (divisions, amendment lifecycle) | T18 | T4,T7 |
| C6 | Kanon 2 Embedder Evaluation (#1 MLEB, NZ retrieval) | T22 | T5 |
| C7 | Pydantic v2 Evaluation (benchmark vs msgspec for API) | T23 | T1 |
| C8 | uv_build Migration (evaluate switching from hatchling) | T23 | T1 |

### ⚪ W — Won't Have (this phase — future)

| ID | Requirement | Rationale |
|----|-------------|-----------|
| W1 | Northflank Preview Deployments | Requires account + infra |
| W2 | Argo CD GitOps Deployer | Requires Kubernetes |
| W3 | Astro Documentation Portal | Requires build pipeline |
| W4 | Mutation Testing in CI | Too expensive; run ad-hoc |
| W5 | Coreference Resolution | Requires annotated NZ dataset |



---

## Runtime Requirements

| Requirement | Version | Purpose | MoSCoW |
|-------------|---------|---------|:------:|
| Python | >=3.13t | Core runtime (PEP 703 free-threaded) | 🔴 M |
| pixi | latest | Multi-language env orchestration | 🔴 M |
| uv | latest | Fast Python package resolution | 🔴 M |
| Rust toolchain | >=1.80 | Maturin builds | 🟡 S |

## Core Dependencies

### NLP & ML Engine

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| spaCy | >=3.7.0 | Syntactic parsing, EntityRuler | 🔴 M |
| transformers | >=4.40.0 | Hugging Face models | 🔴 M |
| torch | >=2.2.0 | PyTorch backend | 🔴 M |
| bitsandbytes | >=0.42.0 | 4-bit/8-bit quantization | 🟡 S |
| datasets | >=2.19.0 | HF dataset loading/uploading | 🔴 M |
| huggingface_hub | >=0.23.0 | HF Hub API client | 🔴 M |
| lingua-language-detector | latest | Te Reo Māori / English detection | 🔴 M |
| accelerate | >=0.27.0 | Multi-GPU training (Track 20) | 🟡 S |
| peft | >=0.8.0 | QLoRA fine-tuning (Track 20) | 🟡 S |
| trl | >=0.8.0 | Transformer RL (Track 20) | 🔵 C |

### Data Processing & Storage

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| polars | >=1.0.0 | Rust-backed DataFrame ops | 🔴 M |
| pyarrow | >=16.0.0 | Arrow/Parquet serialization | 🔴 M |
| narwhals | >=1.0.0 | DataFrame-agnostic compat layer | 🔴 M |
| lancedb | >=0.6.0 | Serverless vector database | 🔴 M |
| faiss-cpu | >=1.8.0 | In-memory similarity search | 🟡 S |
| networkx | >=3.0 | Relational graphing | 🔴 M |
| msgspec | >=0.18.0 | High-performance struct validation | 🔴 M |
| beautifulsoup4 | >=4.12.0 | XML/HTML parsing | 🔴 M |
| lxml | >=5.1.0 | Fast XML processing | 🔴 M |

### Web & API

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| fastapi | >=0.110.0 | Inference API server | 🟡 S |
| uvicorn | >=0.27.0 | ASGI server | 🟡 S |
| gradio | >=4.0.0 | Interactive visualization Spaces | 🟡 S |

### Utilities

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| requests | >=2.31.0 | HTTP client (Zenodo API) | 🔴 M |
| rdflib | >=7.0.0 | RDF/FOAF serialization (Track 16) | 🔵 C |

## Development Dependencies

### Testing

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| pytest | >=8.0 | Test runner | 🔴 M |
| pytest-cov | >=5.0.0 | Coverage reporting | 🔴 M |
| hypothesis | >=6.90 | Property-based testing | 🔴 M |
| mutatest | >=3.0 | Mutation testing (ad-hoc) | ⚪ W |

### Linting, Formatting & Static Analysis

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| ruff | >=0.3.0 | Lint/format/imports (max strict) | 🔴 M |
| pyright | >=1.1.0 | Static type checking (strict) | 🔴 M |
| tach | >=0.5.0 | Module boundary enforcement | 🔴 M |
| import-linter | >=2.0 | Architectural boundary enforcement | 🟡 S |
| complexipy | >=0.2.0 | Cognitive complexity analysis | 🔴 M |
| vale | >=3.0 | Prose linting (docs) | 🟡 S |

### Profiling & Observability

| Package | Version | Purpose | MoSCoW |
|---------|---------|---------|:------:|
| scalene | >=1.5.0 | CPU/memory profiling | 🟡 S |
| opentelemetry-api | latest | Distributed tracing (future) | 🔵 C |

## Hardware Requirements

| Resource | Minimum | Recommended | MoSCoW |
|----------|---------|-------------|:------:|
| RAM | 16 GB | 32 GB+ | 🔴 M |
| GPU | None (CPU) | 1× A100 80GB / H100 | 🟡 S |
| Disk | 10 GB free | 100 GB+ (caches + corpora) | 🔴 M |

## Infrastructure — Future (All ⚪ W)

| Component | Purpose | When |
|-----------|---------|------|
| OpenTelemetry | Distributed tracing | Post Phase II |
| Scaled profiling (6.5GB corpus) | Throughput benchmarks | Post Phase II |
| Northflank | Preview env deployment | Post v2.0 |
| Argo CD | GitOps production deploy | Post v2.0 |
| Astro / Docusaurus | Documentation portal | Post v2.0 |
