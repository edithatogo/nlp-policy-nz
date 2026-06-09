# Product Requirements (MoSCoW)

This document prioritizes the functional and non-functional requirements for the `nlp-policy-nz` unified core pipeline.

---

## 1. Must Have (Critical for MVP)
- **Unified Local Ingestion**: Python script to load and stream NZ Hansard and Legislation datasets from local directories or Hugging Face.
- **spaCy Syntactic Processing**: 
  - Tokenization, sentence segmentation, and lemmatization using `spaCy` v3.
  - Sentence-level chunking with unique structural IDs (e.g., `NZ-ACT-1961-043-SEC-4`, `NZ-HANS-2023-05-12-SP-04`).
- **SOTA Māori Language Guard**:
  - Custom spaCy tokenizer rules to protect key Te Reo Māori vocabulary from subword fragmentation.
  - Unicode normalization (NFC) for macron variations (`ā`, `ē`, `ī`, `ō`, `ū`).
- **Entity Identification (Citations)**:
  - Extracting NZ Act names and references (e.g., "section 4 of the Crimes Act 1961") using a spaCy `EntityRuler` and custom regular expressions.
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
  - Incorporating `faiss-cpu` for zero-database, in-memory semantic similarity search over the Parquet outputs.

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
