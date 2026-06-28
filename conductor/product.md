# Initial Concept

Read the Google Search PDF focusing on the end. Focus on core NLP capabilities for the two libraries (spaCy and Hugging Face/Transformers), extending Legal NLP for `corpus-law-nz` and Parliamentary NLP for `corpus-nz-hansard` using existing repos and the document, using SOTA/bleeding edge, faster/better/more powerful libraries (e.g. swapping in Rust-developed libraries where possible).

# Product Guide: nlp-policy-nz

## 1. Product Vision & Goals
`nlp-policy-nz` is a SOTA, high-performance, unified NLP preprocessing and feature extraction engine written in Python and optimized with Rust-backed libraries. It serves as the shared core pipeline for two downstream application branches:
1. **Legal NLP** ([corpus-law-nz](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/corpus-law-nz)): Extracting statutory hierarchies, citation networks, and binding obligations ("must", "shall").
2. **Parliamentary NLP** ([corpus-nz-hansard](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/corpus-nz-hansard)): Speaker-to-party mapping, political sentiment analysis, and tracking policy debates.

The core goal is to ingest, clean, tokenize, and enrich New Zealand legislative (XML) and parliamentary (JSON/Text) documents using a single, memory-efficient pipeline that outputs standardized Apache Parquet tables. By preserving structural XML tags and utilizing the same syntactic and semantic layers, cross-referencing between Hansard debates and Legislation is made automatic and mathematically aligned.

## 2. Target Users
- **Policy Researchers & Analysts**: Analyzing legislative trends, citation networks, and political discourse in New Zealand.
- **Data Engineers & Data Scientists**: Looking for a highly optimized, local-first dataset preprocessing pipeline for large-scale legal text.
- **Academic & Independent Researchers**: Performing computational linguistics research on NZ law and parliamentary proceedings without expensive cloud resources.

## Phase II Expansion — Upcoming Capabilities

The following are planned for Phase II (Tracks 10-23):

### Advanced NLP Features
- **Deontic Modality Detection** (T10): Extract obligation/permission/prohibition with syntactic scope for binding obligation classification.
- **Temporal Expression Extraction** (T11): TimeML-style date/deadline/period extraction with ISO 8601 normalization.
- **Argument Mining & Stance Detection** (T13): Premise/conclusion identification and pro/con/neutral classification in Hansard debates.
- **Named Entity Resolution** (T12): Link MPs, parties, electorates to Wikidata QIDs.

### Ontology & Schema Enrichment
- **Akoma-Ntoso v3 Full Compliance** (T14): FRBR hierarchy, TLCEvent metadata, amendment/judgment/debate types.
- **PROV-O Provenance** (T15): W3C PROV-O graph for full pipeline traceability.
- **FOAF & SIOC Discourse** (T16): MP FOAF profiles, SIOC debate threading, RDF/Turtle export.
- **Wikidata Knowledge Graph** (T17): OWL mapping, federated SPARQL, JSON-LD export.

### Parliamentary Analytics
- **Voting Record Analysis** (T18): Division parsing, aye/nay votes, amendment lifecycle tracking.

### Model Fine-Tuning
- **NZ Legal NLP Fine-Tuning** (T20): Legal-BERT, Gemma, Phi-4, Qwen, Mistral, MiniCPM5, Liquid LFM, Kimi, Exaone, Jamba, MiniMax.
- **Isaacus Ecosystem Integration** (T22): Open Australian Legal Corpus, MLEB-NZ benchmark, Kanon 2 Embedder, semchunk.
- **Bleeding-Edge Architecture Exploration** (T21): MoR, TTT-Linear/RNN, Mamba-3/SSD, DiffusionGemma, Nex-N2.

### Infrastructure & Quality
- **OpenTelemetry Observability** (T19): Distributed tracing across all pipeline components.
- **Scalene/Memray Profiling** (T19): CPU/memory benchmarks on full 6.5GB corpus.
- **Quality Tooling Overhaul** (T23): ruff max strict, pyright strict, smoke/E2E/integration tests, Codecov.

### Roadmap Notes
- Revisit the T19 profiling benchmark path later, when a supported runtime and an adequate corpus are available. The repo-side observability and benchmark harness are complete; the unfinished profiling pass is a future operational check, not a separate track.

## 3. Core Features & Architecture (Phase I — Complete)
- **Universal Ingestion & Preprocessing**: Abstract, format-agnostic ingestion engine (`UniversalIngestionEngine`) supporting XML, HTML, and JSONL formats using BeautifulSoup4/lxml to parse structures dynamically.
- **Dynamic Metadata Extension Registry**: Custom extension naming layer (`MetaExtensionRegistry`) that registers namespace-prefixed properties in spaCy (e.g. `doc._.meta_country`, `span._.schema_structural_type`) dynamically based on region, country, and target standards to prevent name collisions.
- **Modular spaCy Bridge**: Custom `@Language.component` wrapper (`ModularSpaCyBridgeComponent`) mapping parsed document chunk boundaries to token-level spans.
- **Target Schema Emitter**: Standardized serialization layer (`TargetSchemaEmitter`) supporting multiple target standard exports:
  - **ParlaMint-TEI-Ana**: XML token structure nesting for corpus annotation.
  - **Akoma-Ntoso**: Structured legal block containers.
  - **ParlaCAP-JSONL**: Flattened, analysis-ready format optimized for downstream training of Transformers.
- **SOTA Māori Language Guard**: 
  - **Bilingual Tokenizer & Subword Preservation**: A customized tokenizer that maps and preserves specific Te Reo Māori words (such as *tikanga*, *taonga*, *kāwanatanga*) as atomic tokens rather than splitting them into English-centric subwords.
  - **Macron Normalization Layer**: Standardizes text to correct unicode representations (NFC normalization) to handle macron variations (`Māori` vs `Maori` vs `Maaori`).
  - **Language and Code-Switching Detection**: Custom patterns and sequence classification to detect and tag Te Reo Māori vs English sections within bilingual texts (e.g. Hansard speeches).
- **Syntactic Layer & Matcher (spaCy v3)**: Fast sentence segmentation, token cleaning, and custom pattern matching via a rule-based `Matcher` to extract internal legislative cross-references (e.g. "section 5(2)(b)") and external references.
- **Semantic Layer (Hugging Face Transformers)**: Local semantic embeddings using quantized (4-bit via `bitsandbytes`) SOTA legal models like `Equall/SaulLM-7B` or `nlpaueb/legal-bert-base-uncased`, leveraging Rust-backed fast tokenizers (`use_fast=True`).
- **Memory-Efficient Local Storage**: Outputting unified datasets to compressed Apache Parquet format.
- **Relational Graphing & Search**: In-memory similarity search using FAISS/LanceDB (without external databases) and relational graph modeling using NetworkX to map connections between parliamentary speeches and enacted laws.
- **Zenodo Archive & Release Workflow**: One-step archival of pipeline Parquet outputs to the Zenodo Sandbox (testing) and Zenodo Production (citable DOIs) via the CLI. The `archive-to-zenodo` subcommand uploads a single Parquet file, while the `release` subcommand creates a versioned `.tar.gz` archive (with metadata JSON) and publishes it in a single workflow.
