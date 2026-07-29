# Maturity Dependency Checklist — nlp-policy-nz

> Classifies each dependency category for **nlp-policy-nz** based on current adoption,
> production readiness, and project roadmap alignment.

---

## Classification Values

| Value | Meaning |
|---|---|
| `required` | Adopted, in `pyproject.toml` runtime or dev deps, used in CI |
| `optional` | Documented as candidate; behind extras or non-default workflow |
| `deferred` | Likely useful but blocked by compatibility, CI, maturity, or priority |
| `not_applicable` | Not relevant to this repo's purpose |

---

## Checklist

| Category | Status | Rationale |
|---|---|---|
| Python environment manager (`uv` / `pixi`) | **required** | Both mandated by `requirements.md` (M). `pixi` in `pixi.toml`; `uv` lock committed. CI uses pixi exclusively. |
| Python lint/format (`ruff`) | **required** | M4 in `requirements.md` ("Ruff Max Strict"). Configured at max-strict in `pyproject.toml`. CI gate. |
| Python type checking (`pyright`) | **required** | M5 in `requirements.md` ("pyright Strict Typing"). Configured `typeCheckingMode = "strict"` in `pyproject.toml`. pixi task `typecheck`. |
| Python logging (`loguru`) | **required** | Runtime dependency in `pyproject.toml`. Tool config `logging = "loguru"`. Adopted across all modules. |
| Python CLI UX (`typer` / `rich`) | **deferred** | Track 100 / [#197](https://github.com/edithatogo/nlp-policy-nz/issues/197) (S-ADX-1). CLI still argparse; Typer/Rich planned as Should for operator UX. |
| Config/env loading (`pydantic-settings`) | **deferred** | Track 101 Could (C-QH-1). Env profiles exist; typed settings not yet adopted. |
| Boundary validation (`pydantic` v2) | **optional** | Already used heavily in FOI extraction schemas; msgspec remains hot-path serializer. Maturity checklist previously stale (“deferred”). |
| Hot record serialization (`msgspec`) | **required** | Runtime dependency in `pyproject.toml`. Core to high-throughput pipeline. MoSCoW M. |
| Dataframes (`polars`) | **required** | Runtime dependency. Core DataFrame engine for Parquet operations. MoSCoW M. |
| Analytical vector SQL (`duckdb` / VSS) | **optional** | Track 57 treats DuckDB VSS as an experimental analytics candidate over Parquet/vector arrays, not as the default vector store. |
| Columnar data (`pyarrow` / Parquet) | **required** | Runtime dependency. Core to dataset I/O and HF/DuckDB interoperability. MoSCoW M. |
| JSON schema (`jsonschema`) | **deferred** | Not currently a dependency. nlp-policy-nz uses native msgspec serialization. Would be useful for registry/submission schema contracts (future). |
| HTTP clients (`httpx` / `requests`) | **required** | `requests` is a runtime dependency (Zenodo API, HF Hub). MoSCoW M. `httpx` candidate for new async code paths. |
| Retry/backoff (`tenacity`) | **deferred** | Not currently a dependency. nlp-policy-nz is primarily a processing engine — retry logic is in corpus ingestion repos. |
| HTML parsing (`beautifulsoup4` / `selectolax`) | **required** | `beautifulsoup4` is MoSCoW M for XML/HTML ingestion. `lxml` also runtime dep. `selectolax` deferred pending parser benchmarks. |
| Terminal UI (`rich`) | **optional** | Not a current dependency. Would enhance CLI operator UX (progress bars, formatted output) but not blocking. |
| Checksums / manifests | **deferred** | Product vision includes Zenodo release workflow with manifests. Not implemented yet — deferred to archive/release track. |
| Local vector store (`lancedb`) | **required** | Runtime dependency and default local/serverless vector backend for CLI, API, pipeline search, and RAG wrappers. |
| Service vector DB (`qdrant`) | **optional** | Remote-service semantics only. Generic local vector lifecycle tests should use LanceDB unless a Qdrant deployment requirement is documented. |
| In-memory vector benchmark (`faiss-cpu`) | **optional** | Useful for benchmark comparison, but removed from default Pixi/runtime installs because no default workflow requires it. |
| Local catalog helper (`sqlite-utils`) | **not_applicable** | Removed from default dependency declarations; stdlib `sqlite3` remains enough for extraction catalogs. |
| Embedded key-value store (`rocksdb`) | **not_applicable** | Does not replace Parquet artifacts, LanceDB vector search, or SQLite manifest catalogs for current repo abstractions. |
| Governance orchestration (`haystack-ai`) | **optional** | Track 99 / [#189](https://github.com/edithatogo/nlp-policy-nz/issues/189). Optional pipeline-first audit shell only; spaCy + LanceDB + `PipelineRecord` remain canonical. Subissues [#190](https://github.com/edithatogo/nlp-policy-nz/issues/190)–[#194](https://github.com/edithatogo/nlp-policy-nz/issues/194). |
| Jurisdiction profiles (YAML/JSON) | **deferred** | Track 103 / [#200](https://github.com/edithatogo/nlp-policy-nz/issues/200). NZ+AU adapters exist as Python modules; config-driven profiles not yet shipped. |
| Constrained decoding / GraphRAG / eval harness | **deferred** | Track 105 / [#202](https://github.com/edithatogo/nlp-policy-nz/issues/202). Optional `sota` extras only; never promotion oracles. |
| HF publication (`huggingface_hub` / `datasets`) | **required** | Both are runtime dependencies. Core to model and dataset publishing pipeline. MoSCoW M. Track 100 may move heavy HF/Gradio paths to extras. |
| Archive / DOI (Zenodo / OSF) | **deferred** | Product vision includes Zenodo archive workflow. Currently uses `requests` + REST API ad-hoc. No dedicated adapter package exists yet. Track 104 documents sandbox vs production gates. |

---

## Adoption Summary

| Maturity Band | Count | Categories |
|---|---|---|
| **required** | 11 | env mgr, ruff, pyright, loguru, msgspec, polars, pyarrow, requests, bs4/lxml, lancedb, hf_hub/datasets |
| **optional** | 6 | rich, qdrant, faiss-cpu, duckdb/VSS, haystack-ai (T99), pydantic v2 (FOI schemas) |
| **deferred** | 9 | typer/rich CLI UX, pydantic-settings, jsonschema, tenacity, selectolax, checksums/manifests, Zenodo/OSF, jurisdiction profiles (T103), SOTA extras (T105) |
| **not_applicable** | 2 | sqlite-utils, rocksdb |

> **28 categories assessed.** 11 adopted, 6 optional, 9 deferred, 2 not-applicable.
> Next maturity gates: Phase XV [#196](https://github.com/edithatogo/nlp-policy-nz/issues/196) (Tracks 100–105), selectolax parser benchmarks, Zenodo adapter.
