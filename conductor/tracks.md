# Project Tracks

This file tracks all major tracks for the project. Each track has its own detailed plan in its respective folder.

---

## [x] Track 1: Initialize Workspace Environment & Quality Tooling [b65c685]
*Link: [./conductor/tracks/track1_env_setup_20260609/](./conductor/tracks/track1_env_setup_20260609/)*
- **Dependencies**: None
- **Parallelization Node**: Core Setup Orchestration

## [x] Track 2: Configure External Integrations & Data Sovereignty Registry [b65c685]
*Link: [./conductor/tracks/track2_external_repos_20260609/](./conductor/tracks/track2_external_repos_20260609/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Integration Registry

## [x] Track 3: Implement Māori Language Guard [b65c685]
*Link: [./conductor/tracks/track3_maori_guard_20260609/](./conductor/tracks/track3_maori_guard_20260609/)*
- **Dependencies**: Track 1
- **Parallelization Node**: Linguistic Guard (Can run in parallel with Track 2)

## [x] Track 4: Build Versioned Universal Ingestion Engine & Schema Emitters (v1 & v2) [b65c685]
*Link: [./conductor/tracks/track4_syntactic_layer_20260609/](./conductor/tracks/track4_syntactic_layer_20260609/)*
- **Dependencies**: Track 3
- **Parallelization Node**: Ingestion, Dynamic Registry, and Versioned Schema Emitters

## [x] Track 5: Integrate Semantic Layer & Quantized Embeddings [b65c685]
*Link: [./conductor/tracks/track5_semantic_layer_20260609/](./conductor/tracks/track5_semantic_layer_20260609/)*
- **Dependencies**: Track 3
- **Parallelization Node**: Deep Learning Core

## [x] Track 6: Standardize Output Schema & LanceDB Vector Engine [b65c685]
*Link: [./conductor/tracks/track6_storage_search_20260609/](./conductor/tracks/track6_storage_search_20260609/)*
- **Dependencies**: Track 4, Track 5
- **Parallelization Node**: Storage Engine

## [x] Track 7: Design Downstream API & Multi-Agent Verification [b65c685]
*Link: [./conductor/tracks/track7_downstream_integration_20260609/](./conductor/tracks/track7_downstream_integration_20260609/)*
- **Dependencies**: Track 6, Track 2
- **Parallelization Node**: Downstream FFI & Graph Links

## [x] Track 8: Deploy Hugging Face Datasets & Interactive Visualization Spaces [6ee0627]
*Link: [./conductor/tracks/track8_huggingface_20260612/](./conductor/tracks/track8_huggingface_20260612/)*
- **Dependencies**: Track 7
- **Parallelization Node**: Hugging Face Hub Integration

## [x] Track 9: Establish Citable Zenodo Archives & Release Workflows [6ee0627]
*Link: [./conductor/tracks/track9_zenodo_20260609/](./conductor/tracks/track9_zenodo_20260609/)*
- **Dependencies**: Track 8
- **Parallelization Node**: Zenodo API Deposit Registry



---

## Phase II — Ontology & NLP Feature Expansion

---

## [ ] Track 10: Extract Deontic Modality & Legal Effect
*Link: [./conductor/tracks/track10_deontic_modality_20260613/](./conductor/tracks/track10_deontic_modality_20260613/)*
- **Dependencies**: Track 4, Track 5
- **Parallelization Node**: Legal Effect Analysis
- **Why**: Core requirement for corpus-law-nz — "must/shall/may/must not" binding obligation detection. LKIF ontology categories.

## [ ] Track 11: Temporal Expression Extraction & Time Ontology
*Link: [./conductor/tracks/track11_temporal_ontology_20260613/](./conductor/tracks/track11_temporal_ontology_20260613/)*
- **Dependencies**: Track 4, Track 5
- **Parallelization Node**: Temporal Analysis
- **Why**: Extract dates, deadlines, effective periods from legislation. TimeML/OWL-Time inspired.

## [ ] Track 12: Named Entity Resolution & Wikidata Linking
*Link: [./conductor/tracks/track12_entity_linking_20260613/](./conductor/tracks/track12_entity_linking_20260613/)*
- **Dependencies**: Track 5
- **Parallelization Node**: Knowledge Base Integration
- **Why**: Link MPs, parties, electorates to Wikidata QIDs. Essential for corpus-nz-hansard speaker mapping.

## [ ] Track 13: Argument Mining & Policy Stance Detection
*Link: [./conductor/tracks/track13_argument_stance_20260613/](./conductor/tracks/track13_argument_stance_20260613/)*
- **Dependencies**: Track 5, Track 7
- **Parallelization Node**: Discourse Analysis
- **Why**: Premise/conclusion identification and pro/con/neutral stance in Hansard debates.

## [ ] Track 14: Akoma-Ntoso v3 Schema Compliance & Enrichment
*Link: [./conductor/tracks/track14_akoma_ntoso_v3_20260613/](./conductor/tracks/track14_akoma_ntoso_v3_20260613/)*
- **Dependencies**: Track 4
- **Parallelization Node**: Schema Standards Compliance
- **Why**: Full OASIS AKN v3 compliance — FRBR hierarchy, all document types, TLCEvent metadata.

## [ ] Track 15: PROV-O Provenance Ontology for Pipeline Traces
*Link: [./conductor/tracks/track15_prov_o_provenance_20260613/](./conductor/tracks/track15_prov_o_provenance_20260613/)*
- **Dependencies**: Track 6, Track 9
- **Parallelization Node**: Provenance & Reproducibility
- **Why**: Track pipeline version, model params, timestamps per run. W3C PROV-O JSON-LD sidecar files.

## [ ] Track 16: FOAF & SIOC Ontologies for Parliamentary Discourse
*Link: [./conductor/tracks/track16_faaf_sioc_discourse_20260613/](./conductor/tracks/track16_faaf_sioc_discourse_20260613/)*
- **Dependencies**: Track 7, Track 12
- **Parallelization Node**: Semantic Web & Discourse
- **Why**: MP FOAF profiles, SIOC debate threading, RDF/Turtle export for linked data consumption.

## [ ] Track 17: Wikidata NZ Ontology Integration
*Link: [./conductor/tracks/track17_wikidata_integration_20260613/](./conductor/tracks/track17_wikidata_integration_20260613/)*
- **Dependencies**: Track 12
- **Parallelization Node**: Knowledge Graph
- **Why**: OWL mapping of NZ legal concepts to Wikidata QIDs. Federated SPARQL queries.

## [ ] Track 18: Voting Record Analysis & Amendment Tracking
*Link: [./conductor/tracks/track18_voting_amendments_20260613/](./conductor/tracks/track18_voting_amendments_20260613/)*
- **Dependencies**: Track 4, Track 7
- **Parallelization Node**: Parliamentary Analytics
- **Why**: Parse divisions, aye/nay votes, bill version diffs, amendment lifecycle.

## [ ] Track 19: OpenTelemetry Observability & Performance Benchmarks
*Link: [./conductor/tracks/track19_observability_benchmarks_20260613/](./conductor/tracks/track19_observability_benchmarks_20260613/)*
- **Dependencies**: Track 1, Track 6
- **Parallelization Node**: Infrastructure & Quality
- **Why**: Complete the tech-stack observability layer — OTel spans, Scalene/Memray profiling, CI benchmark gates.

## [ ] Track 20: NZ Legal NLP Model Fine-Tuning Pipeline
*Link: [./conductor/tracks/track20_legal_finetuning_20260613/](./conductor/tracks/track20_legal_finetuning_20260613/)*
- **Dependencies**: Track 5, Track 6
- **Parallelization Node**: Model Fine-Tuning & Domain Adaptation
- **Why**: Fine-tune Legal-BERT, Gemma, Phi-4, Qwen, Mistral, MiniCPM5, Liquid LFM, Kimi, Exaone, Jamba, MiniMax on NZ legal/Hansard corpora across 6 tasks.

## [ ] Track 21: Bleeding-Edge Architecture Exploration
*Link: [./conductor/tracks/track21_bleeding_edge_architectures_20260613/](./conductor/tracks/track21_bleeding_edge_architectures_20260613/)*
- **Dependencies**: Track 20
- **Parallelization Node**: Advanced Architecture Research
- **Why**: Evaluate MoR, TTT-Linear/RNN, Mamba-3/SSD, DiffusionGemma, SambaY, Nex-N2, NexRL, MiniMax-01, NVIDIA Cosmos 3, MiMo-V2.5, Ring, TiRex, DeVestral for transformative efficiency gains in NZ legal NLP.

