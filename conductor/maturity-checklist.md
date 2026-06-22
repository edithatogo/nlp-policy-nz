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
| Python CLI UX (`typer` / `rich`) | **deferred** | CLI entry point exists (`nlp-policy-nz` script) but uses basic argparse + prints. Neither `typer` nor `rich` is a dependency. Worth adding post-Phase II. |
| Config/env loading (`pydantic-settings`) | **deferred** | Not in current dependency tree. No `.env`-based config pattern yet. C7 evaluation (Pydantic v2 bench) must precede adoption. |
| Boundary validation (`pydantic` v2) | **deferred** | C7 in `requirements.md`. `msgspec` is the primary struct-validation tool today. Pydantic v2 needs benchmark justification before adoption. |
| Hot record serialization (`msgspec`) | **required** | Runtime dependency in `pyproject.toml`. Core to high-throughput pipeline. MoSCoW M. |
| Dataframes (`polars`) | **required** | Runtime dependency. Core DataFrame engine for Parquet operations. MoSCoW M. |
| Query validation (`duckdb`) | **not_applicable** | Not in nlp-policy-nz dependency tree. Query validation belongs in corpus repos (`corpus-law-nz`, `corpus-nz-hansard`). |
| Columnar data (`pyarrow` / Parquet) | **required** | Runtime dependency. Core to dataset I/O and HF/DuckDB interoperability. MoSCoW M. |
| JSON schema (`jsonschema`) | **deferred** | Not currently a dependency. nlp-policy-nz uses native msgspec serialization. Would be useful for registry/submission schema contracts (future). |
| HTTP clients (`httpx` / `requests`) | **required** | `requests` is a runtime dependency (Zenodo API, HF Hub). MoSCoW M. `httpx` candidate for new async code paths. |
| Retry/backoff (`tenacity`) | **deferred** | Not currently a dependency. nlp-policy-nz is primarily a processing engine — retry logic is in corpus ingestion repos. |
| HTML parsing (`beautifulsoup4` / `selectolax`) | **required** | `beautifulsoup4` is MoSCoW M for XML/HTML ingestion. `lxml` also runtime dep. `selectolax` deferred pending parser benchmarks. |
| Terminal UI (`rich`) | **optional** | Not a current dependency. Would enhance CLI operator UX (progress bars, formatted output) but not blocking. |
| Checksums / manifests | **deferred** | Product vision includes Zenodo release workflow with manifests. Not implemented yet — deferred to archive/release track. |
| Local vector store (`lancedb`) | **required** | Runtime dependency. Core serverless vector DB. MoSCoW M. |
| Service vector DB (`qdrant`) | **optional** | Candidate per consensus baseline. Not yet a dependency. Benchmarks must justify the switch from `lancedb`. |
| RAG orchestration (`haystack`) | **deferred** | Not a current dependency. Consensus says "nlp-policy-nz prototypes". Suitable for modular RAG experiments behind `[project.optional-dependencies] rag`. |
| HF publication (`huggingface_hub` / `datasets`) | **required** | Both are runtime dependencies. Core to model and dataset publishing pipeline. MoSCoW M. |
| Archive / DOI (Zenodo / OSF) | **deferred** | Product vision includes Zenodo archive workflow. Currently uses `requests` + REST API ad-hoc. No dedicated adapter package exists yet. |

---

## Adoption Summary

| Maturity Band | Count | Categories |
|---|---|---|
| **required** | 10 | env mgr, ruff, pyright, loguru, msgspec, polars, pyarrow, requests, bs4/lxml, lancedb, hf_hub/datasets |
| **optional** | 2 | rich, qdrant |
| **deferred** | 8 | typer/rich CLI UX, pydantic-settings, pydantic v2, jsonschema, tenacity, selectolax, checksums/manifests, haystack, Zenodo/OSF |
| **not_applicable** | 1 | duckdb |

> **22 categories assessed.** 10 adopted, 2 optional, 8 deferred, 1 not-applicable.
> Next maturity gates: pydantic v2 benchmark (C7), selectolax parser benchmarks, Zenodo adapter.
