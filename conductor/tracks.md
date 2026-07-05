# Project Tracks

This file tracks all major tracks for the project. Each track has its own detailed plan in its respective folder.

## Execution Order for Jules

Tracks should be executed in **phase order** (I → II → III → IV → V → VI → VII), with parallelization nodes processed concurrently within each phase:

```
Phase I (Complete — 1-9): Core Pipeline & Integrations
  ├─ 1 (Env Setup) ──► 2 (External Repos) ──► 3 (Māori Guard)
  │                     ├─► 4 (Ingestion) ──► 6 (Storage/Search) ──► 7 (API)
  │                     └─► 5 (Semantic) ────┘                       ├─► 8 (HF Datasets)
  │                                                                  └─► 9 (Zenodo)
  └─ 24 (Multi-Git Mirroring) [runs after 23]

Phase II (In Progress — 10-23): Ontology + Features + Quality
  ├─ Ontology: 10 (Deontic) → 11 (Temporal) → 12 (Entity)
  │             → 13 (Argument) → 14 (AKN v3) → 15 (PROV-O)
  │             → 16 (FOAF/SIOC) → 17 (Wikidata) → 18 (Voting)
  ├─ Fine-Tuning: 20 (Models) → 21 (Architectures) → 22 (Isaacus)
  └─ Quality: 19 (Observability) ──► 23 (Tooling)

Phase III (Planned — 25-37): Ontology + Analytics + Publication
  ├─ Discovery: 25 (Coverage Audit) → 26 (Standards) + 28 (Discovery)
  ├─ Mapping:   27 (RaC Bridge) + 29 (Mapping KG) → 30 (Inference)
  ├─ Ontology:  31 (NZ Ontologies)
  ├─ Analytics: 32 (Corpus Stats) → 33 (Graph/Vector)
  ├─ Protocol:  34 (Publication Protocol)
  └─ Delivery:  35 (Artifacts) → 36 (HF Site) → 37 (Manuscript)

Phase IV (Planned — 38-44): Infrastructure + Automation + Security
  ├─ Quality:   38 (Container) → 39 (Governance) → 40 (Dependency Security)
  └─ Security:  41 (SAST) → 42 (Perf Regression) → 43 (Agentic) → 44 (Data Quality)

Phase V (Planned — 45-46): Release Engineering + Production Maturity
  ├─ 45 (Release Engineering) ──► HF/Zenodo/OSF/PyPI auto-publish
  │   [depends on 8, 9, 24, 36]
  └─ 46 (Production Hardening) ──► API v1/v2, env separation, migration, load test
      [depends on 7, 23, 38, 44]

Phase VI (Planned — 47-50): Cross-Platform + DX + Docs + Compliance
  ├─ 47 (Cross-Platform CI) ──► multi-OS matrix, binary builds
  │   [depends on 1, 23, 38]
  ├─ 48 (Client SDK) ──► Python client, shell completion, Docker Compose
  │   [depends on 7, 38, 46]
  ├─ 49 (Docs Site) ──► MkDocs, API ref, user guides, tutorials, runbook
  │   [depends on 7, 23, 39, 45, 46, 47, 48]
  └─ 50 (Compliance) ──► WCAG 2.1 AA, Privacy Act, a11y CI
      [depends on 36, 44, 46]

Phase VII (Planned — 51-52): Security & Observability
  ├─ 51 (API Security) ──► API key auth, key lifecycle, scopes, audit log
  │   [depends on 7, 45, 46]
  └─ 52 (Observability) ──► JSON logging, RFC 7807 errors, request tracing, metrics, graceful degradation
      [depends on 19, 46, 51]

Phase VIII (Archived — 68, 70-73): Mojo Migration
  ├─ 68 (Mojo Umbrella) [archived] ──► 70 (Readiness Audit) [archived]
  ├─ 70 (Readiness Audit) [archived] ──► 71 (Linux CI Sandbox) [archived]
  ├─ 70 (Readiness Audit) [archived] ──► 72 (Hotspot Benchmark) [archived]
  └─ 70 + 71 + 72 ──► 73 (Optional Acceleration) [archived]

Phase IX (Complete — 69): GitHub Project Synchronization
  └─ 69 (GitHub Project Sync) [historical issue/project synchronization track]

Phase X (Complete — 74-75): NZ Legal/Hansard Evaluation and Fine-Tuning
  ├─ 74 (Held-Out Evaluation Set) [archived]
  └─ 75 (Fine-Tuned Model) [archived]

Phase XI (Planned — 76-80): Executable Rules-as-Code Completion
  ├─ 76 (All NZ Legislation Source Inventory) ──► 77 (Batch RAC Candidate Export)
  ├─ 77 (Batch RAC Candidate Export) ──► 78 (RuleSpec Promotion Contract)
  ├─ 78 (RuleSpec Promotion Contract) ──► 79 (PolicyEngine Executable Pilot)
  └─ 79 (PolicyEngine Executable Pilot) ──► 80 (OpenFisca and Multi-Engine Parity)
```

---

## [x] Track 1: Initialize Workspace Environment & Quality Tooling (archived) [b65c685]
*Link: [./conductor/tracks/archive/track1_env_setup_20260609/](./conductor/tracks/archive/track1_env_setup_20260609/)*
- **Dependencies**: None
- **Parallelization Node**: Core Setup Orchestration

## [x] Track 2: Configure External Integrations & Data Sovereignty Registry (archived) [b65c685]
*Link: [./conductor/tracks/archive/track2_external_repos_20260609/](./conductor/tracks/archive/track2_external_repos_20260609/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Integration Registry

## [x] Track 3: Implement Māori Language Guard (archived) [b65c685]
*Link: [./conductor/tracks/archive/track3_maori_guard_20260609/](./conductor/tracks/archive/track3_maori_guard_20260609/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Linguistic Guard (Can run in parallel with Track 2)

## [x] Track 4: Build Versioned Universal Ingestion Engine & Schema Emitters (v1 & v2) (archived) [b65c685]
*Link: [./conductor/tracks/archive/track4_syntactic_layer_20260609/](./conductor/tracks/archive/track4_syntactic_layer_20260609/)*
- **Dependencies**: Track 3
- **Parallelization Node**: Ingestion, Dynamic Registry, and Versioned Schema Emitters

## [x] Track 5: Integrate Semantic Layer & Quantized Embeddings (archived) [b65c685]
*Link: [./conductor/tracks/archive/track5_semantic_layer_20260609/](./conductor/tracks/archive/track5_semantic_layer_20260609/)*
- **Dependencies**: Track 3
- **Parallelization Node**: Deep Learning Core

## [x] Track 6: Standardize Output Schema & LanceDB Vector Engine (archived) [b65c685]
*Link: [./conductor/tracks/archive/track6_storage_search_20260609/](./conductor/tracks/archive/track6_storage_search_20260609/)*
- **Dependencies**: Track 4, Track 5
- **Parallelization Node**: Storage Engine

## [x] Track 7: Design Downstream API & Multi-Agent Verification (archived) [b65c685]
*Link: [./conductor/tracks/archive/track7_downstream_integration_20260609/](./conductor/tracks/archive/track7_downstream_integration_20260609/)*
- **Dependencies**: Track 6, Track 2
- **Parallelization Node**: Downstream FFI & Graph Links

## [x] Track 8: Deploy Hugging Face Datasets & Interactive Visualization Spaces (archived) [6ee0627]
*Link: [./conductor/tracks/archive/track8_huggingface_20260612/](./conductor/tracks/archive/track8_huggingface_20260612/)*
- **Dependencies**: Track 7
- **Parallelization Node**: Hugging Face Hub Integration

## [x] Track 9: Establish Citable Zenodo Archives & Release Workflows (archived) [6ee0627]
*Link: [./conductor/tracks/archive/track9_zenodo_20260609/](./conductor/tracks/archive/track9_zenodo_20260609/)*
- **Dependencies**: Track 8
- **Parallelization Node**: Zenodo API Deposit Registry



---

## Phase II — Ontology & NLP Feature Expansion

---

## [x] Track 10: Extract Deontic Modality & Legal Effect (archived)
*Link: [./conductor/tracks/archive/track10_deontic_modality_20260613/](./conductor/tracks/archive/track10_deontic_modality_20260613/)*
- **Dependencies**: Track 4, Track 5
- **Parallelization Node**: Legal Effect Analysis
- **Why**: Core requirement for corpus-law-nz — "must/shall/may/must not" binding obligation detection. LKIF ontology categories.

## [x] Track 11: Temporal Expression Extraction & Time Ontology (archived)
*Link: [./conductor/tracks/archive/track11_temporal_ontology_20260613/](./conductor/tracks/archive/track11_temporal_ontology_20260613/)*
- **Dependencies**: Track 4, Track 5
- **Parallelization Node**: Temporal Analysis
- **Why**: Extract dates, deadlines, effective periods from legislation. TimeML/OWL-Time inspired.

## [x] Track 12: Named Entity Resolution & Wikidata Linking (archived)
*Link: [./conductor/tracks/archive/track12_entity_linking_20260613/](./conductor/tracks/archive/track12_entity_linking_20260613/)*
- **Dependencies**: Track 5
- **Parallelization Node**: Knowledge Base Integration
- **Why**: Link MPs, parties, electorates to Wikidata QIDs. Essential for corpus-nz-hansard speaker mapping.

## [x] Track 13: Argument Mining & Policy Stance Detection (archived)
*Link: [./conductor/tracks/archive/track13_argument_stance_20260613/](./conductor/tracks/archive/track13_argument_stance_20260613/)*
- **Dependencies**: Track 5, Track 7
- **Parallelization Node**: Discourse Analysis
- **Why**: Detect Hansard argument components, support/attack relations, issue links, and pro/con/neutral policy stances while keeping gold-label and held-out model gates explicit.

## [x] Track 14: Akoma-Ntoso v3 Schema Compliance & Enrichment (archived)
*Link: [./conductor/tracks/archive/track14_akoma_ntoso_v3_20260613/](./conductor/tracks/archive/track14_akoma_ntoso_v3_20260613/)*
- **Dependencies**: Track 4
- **Parallelization Node**: Schema Standards Compliance
- **Why**: Full OASIS AKN v3 compliance — FRBR hierarchy, all document types, TLCEvent metadata.

## [x] Track 15: PROV-O Provenance Ontology for Pipeline Traces (archived)
*Link: [./conductor/tracks/archive/track15_prov_o_provenance_20260613/](./conductor/tracks/archive/track15_prov_o_provenance_20260613/)*
- **Dependencies**: Track 6, Track 9
- **Parallelization Node**: Provenance & Reproducibility
- **Why**: Track pipeline version, model params, timestamps per run. W3C PROV-O JSON-LD sidecar files.

## [x] Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse (archived)
*Link: [./conductor/tracks/archive/track16_faaf_sioc_discourse_20260613/](./conductor/tracks/archive/track16_faaf_sioc_discourse_20260613/)*
- **Dependencies**: Track 7, Track 12
- **Parallelization Node**: Semantic Web & Discourse
- **Why**: MP FOAF profiles, SIOC debate threading, RDF/Turtle export for linked data consumption.

## [x] Track 17: Wikidata NZ Ontology Integration (archived)
*Link: [./conductor/tracks/archive/track17_wikidata_integration_20260613/](./conductor/tracks/archive/track17_wikidata_integration_20260613/)*
- **Dependencies**: Track 12
- **Parallelization Node**: Knowledge Graph
- **Why**: OWL mapping of NZ legal concepts to Wikidata QIDs. Federated SPARQL queries.

## [x] Track 18: Voting Record Analysis & Amendment Tracking (archived)
*Link: [./conductor/tracks/archive/track18_voting_amendments_20260613/](./conductor/tracks/archive/track18_voting_amendments_20260613/)*
- **Dependencies**: Track 4, Track 7
- **Parallelization Node**: Parliamentary Analytics
- **Why**: Parse divisions, aye/nay votes, bill version diffs, amendment lifecycle.

## [x] Track 19: OpenTelemetry Observability & Performance Benchmarks (archived)
*Link: [./conductor/tracks/archive/track19_observability_benchmarks_20260613/](./conductor/tracks/archive/track19_observability_benchmarks_20260613/)*
- **Dependencies**: Track 1, Track 6
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Complete the tech-stack observability layer. The repo-side OTel spans, profiling wrappers, and CI benchmark gates are complete; the incomplete 1 GiB profiling pass is now a roadmap note rather than a separate track.

---

## Phase III - Ontology, Rules-as-Code, Analytics, and Publication Expansion

---

## [x] Track 28: Ontology Discovery and Intake (archived)
*Link: [./conductor/tracks/archive/track28_ontology_discovery_intake_20260625/](./conductor/tracks/archive/track28_ontology_discovery_intake_20260625/)*
- **Dependencies**: Track 25
- **Parallelization Node**: Standards Discovery
- **Why**: Search for additional relevant legislative, parliamentary, legal, semantic-web, and rules-as-code ontologies and incorporate candidates with provenance and implementation criteria.

## [x] Track 29: Ontology Mapping Knowledge Graph (archived)
*Link: [./conductor/tracks/archive/track29_ontology_mapping_kg_20260625/](./conductor/tracks/archive/track29_ontology_mapping_kg_20260625/)*
- **Dependencies**: Tracks 25-28
- **Parallelization Node**: Ontology Alignment & Visualization
- **Why**: Leverage explicit mappings between ontologies and build them into the system for reasoning, inspection, and knowledge-graph visualization.

## [x] Track 30: Ontology Mapping Inference (archived)
*Link: [./conductor/tracks/archive/track30_ontology_mapping_inference_20260625/](./conductor/tracks/archive/track30_ontology_mapping_inference_20260625/)*
- **Dependencies**: Track 29
- **Parallelization Node**: Mapping Inference
- **Why**: Infer remaining ontology mappings using triangulation, direct matching, fuzzy matching, structural inference, embedding similarity, and LLM-assisted interpretation with reviewable evidence.

## [x] Track 31: New Zealand Data-Driven Ontologies (archived)
*Link: [./conductor/tracks/archive/track31_nz_data_driven_ontologies_20260625/](./conductor/tracks/archive/track31_nz_data_driven_ontologies_20260625/)*
- **Dependencies**: Tracks 25-30
- **Parallelization Node**: NZ Ontology Induction
- **Why**: Induce New Zealand-specific ontology candidates for legal, parliamentary, policy, rules-as-code, graph, vector, and publication applications.

## [x] Track 32: Whole-Corpus Descriptive Statistics (archived)
*Link: [./conductor/tracks/archive/track32_corpus_descriptive_statistics_20260625/](./conductor/tracks/archive/track32_corpus_descriptive_statistics_20260625/)*
- **Dependencies**: Tracks 25-31
- **Parallelization Node**: Corpus Analytics
- **Why**: Produce deterministic corpus-level descriptive statistics, coverage tables, blocker manifests, and publication-ready summaries from supplied PipelineRecord Parquet or local fixtures.

## [x] Track 33: Graph, Vector, and Network Analysis (archived)
*Link: [./conductor/tracks/archive/track33_graph_vector_network_analysis_20260625/](./conductor/tracks/archive/track33_graph_vector_network_analysis_20260625/)*
- **Dependencies**: Tracks 17, 29, 31-32
- **Parallelization Node**: Graph and Embedding Analytics
- **Why**: Analyse the knowledge graph, vector spaces, network structure, ontology links, and graph/vector relationships across the corpus.

## [x] Track 34: Standards-Based Publication Protocol (archived)
*Link: [./conductor/tracks/archive/track34_publication_protocol_20260625/](./conductor/tracks/archive/track34_publication_protocol_20260625/)*
- **Dependencies**: Tracks 24-33
- **Parallelization Node**: Publication Protocol
- **Why**: Document a publication-ready, standards-based protocol covering what the repo has achieved and what remains planned.

## [x] Track 35: Analysis Artifact Execution and Figure Production (archived)
*Link: [./conductor/tracks/archive/track35_analysis_artifact_execution_20260625/](./conductor/tracks/archive/track35_analysis_artifact_execution_20260625/)*
- **Dependencies**: Tracks 32-34
- **Parallelization Node**: Reproducible Artifact Production
- **Why**: Ensure analyses are executed and tables, figures, conceptual diagrams, workflow diagrams, and network diagrams are produced.

## [x] Track 36: Hugging Face Exploration Site (archived)
  *Link: [./conductor/tracks/archive/track36_huggingface_exploration_site_20260625/](./conductor/tracks/archive/track36_huggingface_exploration_site_20260625/)*
- **Dependencies**: Tracks 8, 32-35
- **Parallelization Node**: Public Exploration Interface
- **Why**: Create a Hugging Face Space where ontology, corpus, graph, vector, and publication artefacts can be explored interactively.

## [x] Track 37: Publication Manuscript and Review Agents (archived)
  *Link: [./conductor/tracks/archive/track37_publication_manuscript_review_20260625/](./conductor/tracks/archive/track37_publication_manuscript_review_20260625/)*
- **Dependencies**: Tracks 34-36
- **Parallelization Node**: Manuscript and Review Automation
- **Why**: Create the arXiv-ready manuscript skeleton, supplements, figures, tables, and review-agent loops that score and refine the submission until every aspect exceeds 95/100.

---

## Phase IV — Infrastructure, Automation & Quality Hardening

---

## [x] Track 38: Containerization & Reproducible Execution (archived)
*Link: [./conductor/tracks/archive/track38_containerization_20260626/](./conductor/tracks/archive/track38_containerization_20260626/)*
- **Dependencies**: Track 1, Track 23
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Docker multi-stage builds, .devcontainer for Codespaces/VS Code, docker-compose for local service deps. Makes pipeline portable and CI-reproducible.

## [x] Track 39: Repository Governance & Contribution Framework (archived)
*Link: [./conductor/tracks/archive/track39_governance_contributing_20260626/](./conductor/tracks/archive/track39_governance_contributing_20260626/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Infrastructure & Quality
- **Why**: CONTRIBUTING.md, CODEOWNERS, issue/PR templates, stale-bot, commit message linting, release drafter.

## [x] Track 40: Dependency Automation & Supply Chain Security (archived)
*Link: [./conductor/tracks/archive/track40_dependency_supplychain_20260626/](./conductor/tracks/archive/track40_dependency_supplychain_20260626/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Dependabot/Renovate for automated updates, pip-audit vulnerability scanning, CycloneDX SBOM generation for supply chain transparency.

## [x] Track 41: SAST, Secrets Detection & Security Hardening (archived)
*Link: [./conductor/tracks/archive/track41_sast_security_20260626/](./conductor/tracks/archive/track41_sast_security_20260626/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Bandit + Semgrep SAST scanning, detect-secrets pre-commit hook, security disclosure policy. Catches security issues before production.

## [x] Track 42: Performance Regression CI & Benchmark Baselines (archived)
*Link: [./conductor/tracks/archive/track42_performance_regression_20260626/](./conductor/tracks/archive/track42_performance_regression_20260626/)*
- **Dependencies**: Track 19
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Store benchmark baselines in git, compare PR benchmarks against baselines, fail on >10% regression. Auto-update baselines on master merge.

## [x] Track 43: Agentic Automation & Multi-Agent Orchestration (archived)
*Link: [./conductor/tracks/archive/track43_agentic_automation_20260626/](./conductor/tracks/archive/track43_agentic_automation_20260626/)*
- **Dependencies**: Track 1, Track 23
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Claude Code subagents for PR review + auto-fix CI, Google Jules GPU task dispatch, LLM-as-judge evaluation, conductor advancement automation, self-healing CI.

## [x] Track 44: Data Quality & Pipeline Monitoring (archived)
*Link: [./conductor/tracks/archive/track44_data_quality_monitoring_20260626/](./conductor/tracks/archive/track44_data_quality_monitoring_20260626/)*
- **Dependencies**: Track 6, Track 19
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Input schema validation, data drift detection, per-record quality metrics, pipeline health dashboard, automated degradation alerts.

---

## Phase V — Release Engineering & Production Maturity

---

## [x] Track 45: Release Engineering & Automated Publishing (archived)
*Link: [./conductor/tracks/archive/track45_release_engineering_20260626/](./conductor/tracks/archive/track45_release_engineering_20260626/)*
- **Dependencies**: Tracks 8, 9, 24, 36
- **Parallelization Node**: CI/CD Automation
- **Why**: Semantic versioning from conventional commits, auto-changelog, CI/CD auto-publish to HF datasets/spaces, Zenodo DOIs, OSF archives, and PyPI. Closes the gap between manual CLI publishing and fully automated release pipeline.

## [x] Track 46: Production Hardening & API Maturity (archived)
*Link: [./conductor/tracks/archive/track46_production_hardening_20260626/](./conductor/tracks/archive/track46_production_hardening_20260626/)*
- **Dependencies**: Tracks 7, 23, 38, 44
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Transitions the project from alpha/beta research prototype to mature production system: API versioning (v1/v2), dev/staging/prod environments, database migrations, load/stress testing, feature flags, health endpoints, rate limiting, runbook.

---

## Phase VI — Cross-Platform, Developer Experience, Documentation & Compliance

---

## [x] Track 47: Cross-Platform CI Matrix & Binary Distribution (archived)
*Link: [./conductor/tracks/archive/track47_cross_platform_ci_20260626/](./conductor/tracks/archive/track47_cross_platform_ci_20260626/)*
- **Dependencies**: Tracks 1, 23, 38
- **Parallelization Node**: CI/CD Automation
- **Why**: Current CI only runs on ubuntu-latest. Mature products test on all three target platforms (Windows, macOS, Linux). Adds binary distribution for users who cannot run pixi or Docker.

## [x] Track 48: API Client SDK & Developer Tooling (archived)
*Link: [./conductor/tracks/archive/track48_client_sdk_tooling_20260626/](./conductor/tracks/archive/track48_client_sdk_tooling_20260626/)*
- **Dependencies**: Tracks 7, 38, 46
- **Parallelization Node**: Developer Experience
- **Why**: Build a first-class Python client SDK wrapping the FastAPI server, CLI shell completion, Docker Compose local dev stack, and 5-minute quickstart guide for API consumers.

## [x] Track 49: Documentation Site & Knowledge Base (archived)
*Link: [./conductor/tracks/archive/track49_documentation_site_20260626/](./conductor/tracks/archive/track49_documentation_site_20260626/)*
- **Dependencies**: Tracks 7, 23, 39, 45, 46, 47, 48
- **Parallelization Node**: Developer Experience
- **Why**: Create a dedicated MkDocs/ReadTheDocs site with auto-generated API reference, user guides (ingestion, ontology, search, publishing), architecture docs, Jupyter tutorial notebooks, and operations runbook. Every mature product needs searchable, versioned, auto-generated documentation.

## [x] Track 50: Public Sector Compliance & Accessibility (archived)
*Link: [./conductor/tracks/archive/track50_compliance_accessibility_20260626/](./conductor/tracks/archive/track50_compliance_accessibility_20260626/)*
- **Dependencies**: Tracks 36, 44, 46
- **Parallelization Node**: Compliance & Governance
- **Why**: Ensure the public-facing Gradio Space meets NZ Web Accessibility Standard (WCAG 2.1 AA) and NZ Privacy Act 2020 data governance requirements. A mature government-adjacent product must be accessible and privacy-compliant by default.

---

## Phase VII — Security & Observability

---

## [x] Track 51: API Security & Authentication (archived)
*Link: [./conductor/tracks/archive/track51_api_security_20260626/](./conductor/tracks/archive/track51_api_security_20260626/)*
- **Dependencies**: Tracks 7, 45, 46
- **Parallelization Node**: Security & Observability
- **Why**: Add API key authentication, scope-based authorization, key lifecycle management, audit logging, and security headers to the FastAPI server. Zero auth is the single biggest security gap for any production deployment.

## [x] Track 52: Observability & Error Standardization (archived)
*Link: [./conductor/tracks/archive/track52_observability_20260626/](./conductor/tracks/archive/track52_observability_20260626/)*
- **Dependencies**: Tracks 19, 46, 51
- **Parallelization Node**: Security & Observability
- **Why**: Implement structured JSON logging, RFC 7807 standardized error responses, request ID tracing, Prometheus metrics, graceful model degradation, and ops documentation. Makes the API fully observable and resilient in production.

---

## [x] Track 53: NZ Legal Model Evaluation and Selection (archived)
*Link: [./conductor/tracks/archive/track53_legal_model_evaluation_20260629/](./conductor/tracks/archive/track53_legal_model_evaluation_20260629/)*
- **Dependencies**: Track 20, Track 22, Track 13
- **Parallelization Node**: Model Evaluation and Selection
- **Why**: Compare `isaacus/emubert`, `nlpaueb/legal-bert-base-uncased`, `Equall/Saul-7B-Instruct-v1`, `isaacus/open-australian-legal-llm`, and Kanon-style retrieval candidates for NZ legal NLP model selection and follow-up fine-tuning.

## [x] Track 54: Axiom Foundation Interoperability (archived)
*Link: [./conductor/tracks/archive/track54_axiom_foundation_interop_20260629/](./conductor/tracks/archive/track54_axiom_foundation_interop_20260629/)*
- **Dependencies**: Tracks 18, 22, 27
- **Parallelization Node**: External Legal Source and Rules-as-Code Interoperability
- **Why**: Capture selective Axiom Foundation integration as repo-side source-section metadata, source hash staleness checks, RuleSpec identity bridge, bill/Hansard linkage scaffolding, and explicit documentation of which Axiom repositories should be used as code, design reference, future ideas, or historical context.

## [x] Track 55: Broad Legislation Extraction Framework (archived)
*Link: [./conductor/tracks/archive/track55_broad_legislation_extraction_framework_20260630/](./conductor/tracks/archive/track55_broad_legislation_extraction_framework_20260630/)*
- **Dependencies**: Tracks 4, 10, 11, 14, 15, 18, 26, 27, 54
- **Parallelization Node**: Source-Grounded Legislative Extraction
- **Why**: Promote rules-as-code from a standalone bridge into one output family of a broader source-grounded extraction system covering definitions, obligations, powers, conditions, exceptions, dates, entities, amendments, commencement, repeal, penalties, delegations, review rights, and traceable manifests.

## [x] Track 56: Rust-Accelerated Extraction Runtime (archived)
*Link: [./conductor/tracks/archive/track56_rust_accelerated_extraction_runtime_20260630/](./conductor/tracks/archive/track56_rust_accelerated_extraction_runtime_20260630/)*
- **Dependencies**: Tracks 21, 23, 42, 55
- **Parallelization Node**: Performance and Runtime Modernization
- **Why**: Evaluate Pydantic-core, msgspec, orjson, Polars/Arrow, Rust tokenizers, and possible PyO3/maturin extensions for extraction performance while keeping the Python API and downstream export schemas stable.

---

## Phase VIII — Mojo Migration

---

## [x] Track 68: Mojo Runtime Feasibility for Hot Python Paths (archived)
*Link: [./conductor/tracks/archive/track68_mojo_runtime_feasibility_20260701/](./conductor/tracks/archive/track68_mojo_runtime_feasibility_20260701/)*
- **Dependencies**: Tracks 21, 23, 42, 56, 67
- **Parallelization Node**: Experimental Runtime Strategy
- **Why**: Maintain the umbrella decision record for introducing Mojo as an optional Linux GitHub Actions acceleration path, while keeping concrete work split into Tracks 70-73.

## [x] Track 70: Mojo Readiness Audit (archived)
*Link: [./conductor/tracks/archive/track70_mojo_readiness_audit_20260702/](./conductor/tracks/archive/track70_mojo_readiness_audit_20260702/)*
- **Dependencies**: Tracks 21, 23, 42, 56, 67, 68
- **Parallelization Node**: Mojo Toolchain Readiness
- **Why**: Verify OS support, packaging, licensing, GitHub Actions install path, Pixi/uv compatibility, and candidate kernel shortlist before any runtime code changes. The readiness audit is complete and the historical record now lives in the archive tree.

## [x] Track 71: Mojo Linux CI Sandbox (archived)
*Link: [./conductor/tracks/archive/track71_mojo_linux_ci_sandbox_20260702/](./conductor/tracks/archive/track71_mojo_linux_ci_sandbox_20260702/)*
- **Dependencies**: Track 70
- **Parallelization Node**: Optional Linux Runtime Sandbox
- **Why**: Add an optional Linux-only Mojo experiment sandbox and non-blocking CI path after readiness criteria pass, without touching production imports. The sandbox is complete and now lives in the archive tree.

## [x] Track 72: Mojo Hotspot Benchmark (archived)
*Link: [./conductor/tracks/archive/track72_mojo_hotspot_benchmark_20260702/](./conductor/tracks/archive/track72_mojo_hotspot_benchmark_20260702/)*
- **Dependencies**: Tracks 19, 42, 56, 67, 70
- **Parallelization Node**: Mojo Benchmark Governance
- **Why**: Profile current hot paths, benchmark Mojo candidate kernels, compare against Python/Rust/Polars alternatives, and record go/no-go evidence.

## [x] Track 73: Mojo Optional Acceleration (archived)
*Link: [./conductor/tracks/archive/track73_mojo_optional_acceleration_20260702/](./conductor/tracks/archive/track73_mojo_optional_acceleration_20260702/)*
- **Dependencies**: Tracks 70, 71, 72
- **Parallelization Node**: Optional Mojo Runtime Integration
- **Why**: Integrate one proven private Mojo kernel behind optional feature detection and Python fallback only if Track 72 meets the roadmap promotion threshold; otherwise record a deferral decision.

---

## Phase IX — GitHub Project Synchronization

---

## [x] Track 69: GitHub Project and Conductor Issue Synchronization (archived)
*Link: [./conductor/tracks/archive/track69_github_project_sync_20260701/](./conductor/tracks/archive/track69_github_project_sync_20260701/)*
- **Dependencies**: Tracks 23, 39, 45, 57-68
- **Parallelization Node**: Repository Governance and Planning Operations
- **Why**: Keep the Conductor roadmap mirrored into GitHub issues and GitHub Projects with stable phase, status, dependency, and path metadata while preserving the completed track as a historical record.

---

## Phase X — NZ Legal/Hansard Evaluation and Fine-Tuning

---

## [x] Track 74: NZ Legal/Hansard Held-Out Evaluation Set (archived)
*Link: [./conductor/tracks/archive/track74_nz_legal_hansard_evaluation_set_20260704/](./conductor/tracks/archive/track74_nz_legal_hansard_evaluation_set_20260704/)*
- **Dependencies**: Tracks 13, 19, 20, 23, 53
- **Parallelization Node**: Model Evaluation Data Infrastructure
- **Why**: Create a held-out NZ legal/Hansard evaluation set with leakage controls, provenance, and stable metrics to gate model selection and future fine-tuning.

## [x] Track 75: NZ Legislation/Hansard Fine-Tuned Model (archived)
*Link: [./conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/](./conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/)*
- **Dependencies**: Tracks 74, 20, 53
- **Parallelization Node**: Model Fine-Tuning and Evaluation
- **Why**: Fine-tune a NZ legislation/Hansard model only after the held-out evaluation set establishes a defensible baseline and promotion threshold.

---

## Phase XI — Executable Rules-as-Code Completion

---

## [~] Track 76: All NZ Legislation Source Inventory
*Link: [./conductor/tracks/track76_all_nz_legislation_source_inventory_20260705/](./conductor/tracks/track76_all_nz_legislation_source_inventory_20260705/)*
- **Dependencies**: Tracks 4, 14, 23, 32, 54, 55
- **Parallelization Node**: Full-Corpus Source Readiness
- **Why**: Create the canonical source inventory required before this repository can claim it processes all New Zealand legislation for downstream rules-as-code use.

## [ ] Track 77: Batch Rules-as-Code Candidate Export
*Link: [./conductor/tracks/track77_batch_rules_as_code_candidate_export_20260705/](./conductor/tracks/track77_batch_rules_as_code_candidate_export_20260705/)*
- **Dependencies**: Tracks 10, 11, 12, 14, 15, 18, 26, 27, 54, 55, 56, 76
- **Parallelization Node**: Rules-as-Code Candidate Generation
- **Why**: Promote the single-section `rac-export` bridge into a batch source-grounded candidate pipeline over the all-legislation inventory.

## [ ] Track 78: RuleSpec Promotion Contract
*Link: [./conductor/tracks/track78_rulespec_promotion_contract_20260705/](./conductor/tracks/track78_rulespec_promotion_contract_20260705/)*
- **Dependencies**: Tracks 27, 54, 55, 76, 77
- **Parallelization Node**: Reviewed RuleSpec Handoff
- **Why**: Define the fail-closed review and handoff contract that turns NLP-generated RAC candidates into RuleSpec-ready artifacts without making this repo the executable rules runtime.

## [ ] Track 79: PolicyEngine Executable Pilot
*Link: [./conductor/tracks/track79_policyengine_executable_pilot_20260705/](./conductor/tracks/track79_policyengine_executable_pilot_20260705/)*
- **Dependencies**: Tracks 7, 10, 11, 15, 20, 23, 27, 53, 74, 75, 77, 78
- **Parallelization Node**: PolicyEngine Runtime Pilot
- **Why**: Generate and execute the first reviewed PolicyEngine package from promoted NZ legislation handoff artifacts, proving the primary downstream runtime path.

## [ ] Track 80: OpenFisca and Multi-Engine Parity
*Link: [./conductor/tracks/track80_openfisca_multi_engine_parity_20260705/](./conductor/tracks/track80_openfisca_multi_engine_parity_20260705/)*
- **Dependencies**: Tracks 46, 50, 52, 78, 79
- **Parallelization Node**: Multi-Engine Rules-as-Code Validation
- **Why**: Add OpenFisca export and deterministic parity reporting after the PolicyEngine pilot is proven, then document how other engines should be onboarded.
