# Product Requirements (MoSCoW)

This document prioritizes the functional and non-functional requirements for the `nlp-policy-nz` unified core pipeline.

---

## 1. Must Have (Critical for MVP)
- **Universal Ingestion Engine**:
  - Abstract parser (`UniversalIngestionEngine`) with subclasses for XML, HTML, and JSONL format ingestion.
- **Dynamic Metadata Registry**:
  - Namespace-safe property register (`MetaExtensionRegistry`) mapping parameters (e.g. `COUNTRY`, `TARGET_SCHEMA_STANDARD`) dynamically.
- **Modular spaCy Bridge**:
  - Custom pipeline component (`ModularSpaCyBridgeComponent`) mapping document chunk boundaries onto token-level Spans.
- **Target Schema Emitter**:
  - Serialization layer (`TargetSchemaEmitter`) generating valid ParlaMint-TEI-Ana XML, Akoma-Ntoso legal blocks, and ParlaCAP-JSONL output arrays.
- **PCO Legislative XML Ingestion**: 
  - XML parser utilizing BeautifulSoup/lxml to parse structure tags (`<act>`, `<part>`, `<section>`, `<heading>`, `<para>`).
  - Mapping tag-based hierarchical boundaries to raw character offsets.
- **spaCy Structure Injector**:
  - Custom `nz_xml_structure_injector` pipeline component mapping XML character boundaries to token-level Spans.
  - Custom spaCy `Span` metadata extensions (`nz_element_type`, `nz_element_id`, `nz_element_title`) to preserve structural contexts.
- **spaCy Cross-Reference Matcher**:
  - Custom `nz_cross_reference_matcher` rule-based matcher to extract references like "section 5(2)(b)" or "Part 3" from clean text.
- **Unified Local Ingestion**: Python script to load and stream NZ Hansard and Legislation datasets from local directories or Hugging Face.
  - Optional `UnstructuredIngestionEngine` adapter for messy PDF/DOCX/HTML inputs, enabled only through the `unstructured` extra or an explicit feature flag.
  - Canonical XML, Akoma-Ntoso, and legislation source parsers remain the default and must not be replaced by the adapter.
- **SOTA Māori Language Guard**:
  - Custom spaCy tokenizer rules to protect key Te Reo Māori vocabulary from subword fragmentation.
  - Unicode normalization (NFC) for macron variations (`ā`, `ē`, `ī`, `ō`, `ū`).
- **Apache Parquet Storage**:
  - Exporting processed datasets into memory-efficient, compressed `.parquet` files containing structural fields, cleaned tokens, and extracted act citations.
- **Local Git-Installable Package**:
  - Restructure the core pipeline as an installable Python package (`nlp_policy_nz`) so neighboring repositories can import it directly.

## 2. Should Have (High Priority)
- **Local Hugging Face Semantic Embeddings**:
  - Extracting dense vector representations for text chunks using SOTA legal models (e.g., `Equall/SaulLM-7B` quantized to 4-bit, or `nlpaueb/legal-bert-base-uncased`).
  - Leveraging fast Rust-backed Hugging Face tokenizers (`use_fast=True`).
- **Code-Switching Detection**:
  - Automatically classification of text blocks/sentences as English or Te Reo Māori to enable targeted processing.
- **Local Semantic Search Indexing**:
  - Incorporating LanceDB as the default zero-service semantic search index over Parquet outputs, with `faiss-cpu` retained only as an optional benchmark/comparison extra.
- **Fail-closed Governance Rights Gate (Track 99)**:
  - Restricted / Māori / sovereign `access_class` values (case-insensitive) require `rights_cleared: true` before indexing or extractive QA.
- **Verbatim Extractive Audit Answers (Track 99)**:
  - Answers must be source substrings with offsets; generative defaults banned on restricted paths.
- **Non-authoritative Faithfulness Metric (Track 99)**:
  - Local ExactMatch / SAS-proxy scorecards only; FaithfulnessEvaluator must not gate promotion or OIA evidence.
- **No Default Haystack Import (Track 99)**:
  - Importing `nlp_policy_nz` must not load `haystack-ai`.
- **Phase XV Adoption Musts (Tracks 100–105 / [#196](https://github.com/edithatogo/nlp-policy-nz/issues/196))**:
  - Fixture-first adopter path without Docker/Qdrant (T100 / [#197](https://github.com/edithatogo/nlp-policy-nz/issues/197)).
  - Slim default install; heavy Gradio/ML behind extras (T100).
  - Core `universal_framework` under coverage gate; Compose/prod API auth on (T101 / [#198](https://github.com/edithatogo/nlp-policy-nz/issues/198)).
  - Machine-checkable adoption readiness coordinating [#132](https://github.com/edithatogo/nlp-policy-nz/issues/132)/[#133](https://github.com/edithatogo/nlp-policy-nz/issues/133)/[#144](https://github.com/edithatogo/nlp-policy-nz/issues/144) (T102 / [#199](https://github.com/edithatogo/nlp-policy-nz/issues/199)).
  - Versioned jurisdiction profiles + parameterized shared schema; fail-closed unknown profiles (T103 / [#200](https://github.com/edithatogo/nlp-policy-nz/issues/200)).
  - PR CI fast lane vs nightly full matrix; publish sandbox vs production honesty (T104 / [#201](https://github.com/edithatogo/nlp-policy-nz/issues/201)).
  - Bleeding-edge stacks optional-only; eval harness never promotion oracle (T105 / [#202](https://github.com/edithatogo/nlp-policy-nz/issues/202)).

## 3. Could Have (Desirable but Deferred)
- **NetworkX Relational Graph**:
  - Building in-memory relationship graphs (e.g., MP -> Bill -> Act) to visualize parliamentary debates linking to statutes.
- **CI/CD Integration**:
  - GitHub Action to automate tests and package publishing/checks.
- **Optional Haystack Governance Orchestration (Track 99)**:
  - Pure-Python Haystack-compatible component DAG under `orchestration/haystack/` for typed audit shells, legal-structure indexing, extractive span QA, and local ExactMatch/SAS-proxy scorecards.
  - Optional extras `rag` / `orchestration` may install `haystack-ai>=2.0.0`; default Pixi/CI must not require it.
  - Decision record: `docs/haystack-governance-decision.md`; sovereign deploy checklist: `docs/haystack-sovereign-deploy.md`.
- **Phase XV Should/Could (Tracks 100–105)**:
  - Typer/Rich CLI; jurisdiction onboarding cookbook; constrained decoding / hybrid GraphRAG / MCP contract spikes behind extras.
  - Docling compare, C2PA sidecars, ONNX/Candle probes as Could-only evidence notes.

## 4. Won't Have (Out of Scope for Core Pipeline)
- **External Database Infrastructure**:
  - No deployment of vector databases (Pinecone, Qdrant) or graph databases (Neo4j) to minimize engineering overhead and cost.
- **Web-based User Interface**:
  - Interface visualization tools are out of scope; visualization will be handled downstream or via notebook scripts.
- **Haystack as Required Runtime**:
  - Do not make `haystack-ai` a required dependency or replace spaCy / LanceDB / `PipelineRecord` as canonical engines.
- **Generative Cloud Defaults on Sovereign Data**:
  - Restricted, Māori, and sovereign paths must not default to generative cloud LLMs; LLM FaithfulnessEvaluator is non-authoritative for promotion or OIA evidence.
- **Phase XV Won't**:
  - Do not claim FOI/legal promotion from Tracks 100–105 alone.
  - Do not make SOTA extras required runtimes.
  - Do not imply cross-jurisdiction equivalence without explicit crosswalks (#144).
  - Do not lower coverage `fail_under` to hide framework gaps.
