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
  - Incorporating `faiss-cpu` / `lancedb` for zero-database, in-memory semantic similarity search over the Parquet outputs.

## 3. Could Have (Desirable but Deferred)
- **NetworkX Relational Graph**:
  - Building in-memory relationship graphs (e.g., MP -> Bill -> Act) to visualize parliamentary debates linking to statutes.
- **CI/CD Integration**:
  - GitHub Action to automate tests and package publishing/checks.

## 4. Won't Have (Out of Scope for Core Pipeline)
- **External Database Infrastructure**:
  - No deployment of vector databases (Pinecone, Qdrant) or graph databases (Neo4j) to minimize engineering overhead and cost.
- **Web-based User Interface**:
  - Interface visualization tools are out of scope; visualization will be handled downstream or via notebook scripts.
