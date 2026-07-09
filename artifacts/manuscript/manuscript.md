# nlp-policy-nz: Evidence-bounded NLP infrastructure for New Zealand legal and policy corpora

## Abstract

We present `nlp-policy-nz`, a reproducible NLP pipeline for New Zealand legislation, Hansard, ontology mapping, graph/vector analysis, and publication packaging. The current submission is evidence-bounded: repo-side artifacts cover deterministic fixtures, checked-in ontology manifests, publication protocols, figures, tables, and an exploration Space, while full-corpus and live-publication claims remain explicit gates.

## Introduction

New Zealand legal and policy text combines legislation, parliamentary debate, Te Reo Maori concepts, public-sector metadata standards, and rules-as-code requirements. The project provides a shared core that makes those materials inspectable through structured extraction, ontology alignment, and release-oriented evidence bundles.

## Methods

The pipeline uses deterministic fixture inputs and checked-in manifests to document corpus statistics, ontology coverage, graph/vector outputs, and release protocols. Track 34 maps 14 publication claims to evidence states; Track 35 generates 12 tables, figures, and diagrams; Track 36 exposes those outputs through a Hugging Face Space.

## Interfaces and operationalization

The repository is designed to be consumed through thin, stable surfaces rather than ad hoc notebooks. The CLI remains the primary local and GitHub Actions entrypoint, the HTTP API exposes programmatic access, the Python SDK mirrors the public API, and MCP provides a read-only agent-facing surface. Downstream policy-engine integrations should consume the repo through these surfaces or through checked-in artifacts, not by depending on private implementation details.

## Comparative tooling and deployment choices

The paper should include a compact comparison matrix that explains current defaults, alternatives under review, and the reason each choice is framed the way it is:

| Concern | Current repo choice | Alternatives under review | Paper framing |
| --- | --- | --- | --- |
| Vector storage | LanceDB-first local store | Qdrant service semantics, DuckDB vector experimentation | Default to local, deterministic, CI-friendly execution; keep remote service semantics optional. |
| Tabular transforms | Polars and Arrow-backed transforms | pandas, DuckDB analytics paths | Emphasize fast, reproducible local transforms and deterministic artifact generation. |
| Ingestion and extraction | Repo-native parsers and checked-in fixtures | Unstructured-style generic ingestion | Prefer source-specific parsers where they preserve provenance and make CI simpler. |
| Acceleration | Python baseline with optional Mojo sandbox and optional model-serving lanes | Pure-Python only, always-remote inference | Stage acceleration behind evidence so the paper does not depend on experimental runtime assumptions. |
| Automation surface | CLI, API, SDK, MCP, GitHub Actions | Notebook-only workflows | Present the repository as an executable system with stable interfaces, not as a one-off notebook stack. |

## Results

The protocol currently records 9 repo-evidence claims, 3 blockers, and 1 external gates. The manuscript package includes generated tables, figure references, a supplement skeleton, arXiv requirements, offline review-agent score records, and an explicit claims-to-evidence boundary for publication claims.

## Discussion

The central design decision is to separate reproducible repo evidence from claims that require full-corpus exports, credentials, or external service execution. This prevents overclaiming while preserving a clear path to publication once canonical data exports are supplied. A second design choice is to keep adjacent datasets and downstream consumers loosely coupled: the paper should explain whether a workflow is run from this repository, calls into this repository as a library or service, or consumes a checked-in dataset exported by it.

## Limitations

Full-corpus statistics, live Hugging Face or Zenodo publication evidence, production-scale graph/vector analyses, and downstream system evaluations remain gated. The review loop is deterministic and offline; live external reviewer agents are intentionally not asserted as completed evidence. The paper should also state the main threats to validity explicitly: fixture bias, corpus incompleteness, label drift, benchmark instability, and mirror drift.

## Data and code availability

The repository ships the core code, checks, fixtures, generated manuscript artifacts, publication protocol artifacts, and interface contracts required to reproduce the current evidence-bounded results from a clean checkout. Optional backends and accelerators remain behind feature detection or environment-specific extras, and the paper should identify them as such. Downstream datasets or full-corpus inputs are not embedded in the repository unless they are explicitly checked in and referenced by the relevant track evidence.

## Decision appendix

| Topic | Current decision | Why |
| --- | --- | --- |
| Default vector store | LanceDB | Keeps the local and GitHub Actions path deterministic and low-friction. |
| Remote vector backend | Qdrant optional | Preserves deployment flexibility without making service semantics the baseline. |
| Tabular analysis | Polars / Arrow-first | Provides a fast and reproducible local analysis path. |
| Generic ingestion | Optional future adapter | Useful if it proves provenance-safe, but not required for the current paper claims. |
| Acceleration | Staged, evidence-gated | Mojo and other accelerators should be proven before they are presented as baseline dependencies. |
| Downstream reuse | CLI, API, SDK, MCP, or exported artifacts | Makes the operating model explicit for GitHub Actions and adjacent datasets. |

## Conclusion

`nlp-policy-nz` provides an auditable scaffold for publication-grade legal NLP infrastructure. The next publication step is to replace fixture-bounded sections with canonical full-corpus outputs, rerun the same review loop against those artifacts, and add a comparative evaluation table that justifies the chosen local tooling against the main alternatives.
