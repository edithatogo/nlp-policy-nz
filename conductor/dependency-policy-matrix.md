# Dependency Policy Matrix — nlp-policy-nz

> Consensus baseline applied per Track `dependency_consensus_python314_20260614`.
> Each category classified for **nlp-policy-nz specifically** with rationale.

---

## Classification Values

| Value | Meaning |
|---|---|
| `required` | Must be installed and enforced in this repo |
| `optional` | Useful behind extras, optional workflow, or non-default track |
| `deferred` | Likely useful but blocked by compatibility, CI, maturity, or priority |
| `not_applicable` | Not relevant to this repo's purpose |

---

## Matrix

| Category | Candidate(s) | Classification | Rationale |
|---|---|---|---|
| Python environment manager | `uv` / `pixi` | **required** | Both mandated by requirements.md (M items). `pixi` for conda-forge/GPU/native reproducibility; `uv` for fast lock/sync and CI. |
| Python lint/format | `ruff` | **required** | M4 in requirements.md ("Ruff Max Strict"). Already at max-strict selection in `pyproject.toml`. |
| Python type checking | `ty` / `pyright` | **required** | M5 in requirements.md ("pyright Strict Typing"). Using `pyright` with `typeCheckingMode = "strict"`. |
| Python logging | `loguru` | **required** | Runtime dependency in `pyproject.toml`. Tool config `[tool.legal_nz] logging = "loguru"`. |
| Python CLI UX | `typer` / `rich` | **optional** | CLI entry point exists (`nlp-policy-nz` script) but neither `typer` nor `rich` is currently a dependency. Worth adding — deferred to a dedicated UX track. |
| Config/env loading | `pydantic-settings` | **optional** | Not in current dependency tree. Would be useful for typed env/config but not yet adopted. |
| Boundary validation | `pydantic v2` | **optional** | C7 in requirements.md: "Pydantic v2 Evaluation (benchmark vs msgspec for API)". `msgspec` is the primary struct validation tool. Pydantic is candidate after benchmarking. |
| Hot record serialization | `msgspec` | **required** | Runtime dependency in `pyproject.toml`. Core to high-throughput pipeline. MoSCoW M. |
| Dataframes | `polars` | **required** | Runtime dependency. Core DataFrame engine for Parquet operations. MoSCoW M. |
| Corpus browser dataframe boundary | `polars` core + `pandas` stats/UI boundary | **required** | Track 59 keeps Parquet load and chunk search on Polars internally while preserving the public Gradio/pandas contract. The small stats aggregation remains pandas-first because the benchmark does not justify the conversion overhead. |
| Query / vector analytics | `duckdb` + VSS | **experimental** | Candidate for follow-up analytics over Parquet/vector arrays, not default vector search. |
| Columnar data | `pyarrow` / Parquet | **required** | Runtime dependency. Core to dataset I/O and HF/DuckDB compatibility. MoSCoW M. |
| Vector store | `lancedb` | **required** | Default local/serverless vector backend for CLI, API, pipeline search, and RAG workflows. |
| Vector service | `qdrant-client` | **optional** | Remote-service semantics only; generic local vector lifecycle coverage belongs to LanceDB. |
| Vector benchmark | `faiss-cpu` | **optional/dev** | Benchmark comparison backend; not required for default ingestion, extraction, API, or search. |
| Local catalog helper | `sqlite-utils` | **not_applicable** | No current import path requires it; stdlib `sqlite3` remains enough for extraction catalogs, so the dependency is removed. |
| Embedded key-value store | RocksDB | **not_applicable** | Does not replace Parquet artifacts, LanceDB vector search, or SQLite manifest catalogs. |
| JSON schema | `jsonschema` | **optional** | Not currently a dependency. nlp-policy-nz uses native serialization (msgspec, Parquet). Would be useful for registry/submission schema contracts (future). |
| HTTP clients | `httpx` / `requests` | **required** | `requests` is a runtime dependency (Zenodo API, HF Hub). MoSCoW M. Keep `requests`; consider `httpx` for new async code paths. |
| Retry/backoff | `tenacity` | **deferred** | Not currently a dependency. Would be useful for resilient external API calls (Zenodo, HF Hub), but nlp-policy-nz is primarily a processing engine — retry logic is in corpus ingestion repos. |
| HTML parsing | `beautifulsoup4` / `selectolax` | **required** | `beautifulsoup4` is MoSCoW M for XML/HTML ingestion. `selectolax` is deferred until parser-parity benchmarks prove it beats bs4 for NZ legislation sources. |
| Messy document partitioning | `unstructured` | **optional** | Useful for fallback ingestion of PDFs, DOCX, HTML, and scans, but it must remain behind an explicit extra or feature flag so canonical legislative parsers stay authoritative. |
| Terminal UI | `rich` | **optional** | Not a current dependency. Would enhance CLI operator UX (progress bars, formatted output) but not blocking. |
| Checksums/manifests | repo-local utilities | **deferred** | Product vision includes Zenodo release workflow with manifests. Not implemented yet — deferred to archive/release track. |
| RAG orchestration | `haystack` | **optional** | Consensus says "nlp-policy-nz prototypes". Not a current dependency. Suitable for modular RAG experiments — adopt behind `[project.optional-dependencies] rag`. |
| HF publication | `huggingface_hub` / `datasets` | **required** | Both are runtime dependencies. Core to model and dataset publishing pipeline. MoSCoW M. |
| Archive/DOI | Zenodo / OSF | **deferred** | Product vision includes Zenodo archive workflow, but no dedicated adapter package exists yet. Uses `requests` + REST API currently. |
| ML training | `torch`, `transformers`, `bitsandbytes`, `flash-attn`, etc. | **required** | Core to nlp-policy-nz's purpose. `torch` + `transformers` are M; `bitsandbytes` is S; training extras (`accelerate`, `peft`, `trl`, `flash-attn`) are optional extras. |
| Profiling | `scalene`, `memray` | **optional** | S6 in requirements.md ("Scalene/Memray Profiling") — important but not blocking. In dev extras. |
| Benchmarking | `pytest-benchmark` | **optional** | In dev dependencies. Used for performance regression detection. |
| Telemetry | `opentelemetry` | **optional** | S5 ("OpenTelemetry Tracing") in requirements.md. SDK is in runtime deps, but infra is deferred to post-Phase II. |

---

## Guardrails Applied

| Rule | Applies to nlp-policy-nz? |
|---|---|
| Do not add heavy ML deps to corpus repos | ✅ nlp-policy-nz owns the ML stack |
| Keep RAG orchestration in nlp-policy-nz | ✅ haystack is `optional` here |
| Keep vector-store experiments centralised in nlp-policy-nz | ✅ LanceDB is `required`; Qdrant, FAISS, and DuckDB VSS are optional/experimental |
| Prefer repo-local utilities over root imports | ✅ No root-code imports in this matrix |
| Use `selectolax` only after parser benchmarks | ✅ Deferred — bs4 is required |
| Keep `torch`/`transformers`/`bitsandbytes`/`faiss-cpu` mainly in nlp-policy-nz | ✅ ML deps stay here; FAISS is benchmark/dev optional only |
