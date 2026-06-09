# Initial Concept

Read the Google Search PDF focusing on the end. Focus on core NLP capabilities for the two libraries (spaCy and Hugging Face/Transformers), extending Legal NLP for `corpus-law-nz` and Parliamentary NLP for `corpus-nz-hansard` using existing repos and the document, using SOTA/bleeding edge, faster/better/more powerful libraries (e.g. swapping in Rust-developed libraries where possible).

# Product Guide: nlp-policy-nz

## 1. Product Vision & Goals
`nlp-policy-nz` is a SOTA, high-performance, unified NLP preprocessing and feature extraction engine written in Python and optimized with Rust-backed libraries. It serves as the shared core pipeline for two downstream application branches:
1. **Legal NLP** ([corpus-law-nz](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/corpus-law-nz)): Extracting statutory hierarchies, citation networks, and binding obligations ("must", "shall").
2. **Parliamentary NLP** ([corpus-nz-hansard](file:///C:/Users/60217257/OneDrive%20-%20Flinders/repos/corpus-nz-hansard)): Speaker-to-party mapping, political sentiment analysis, and tracking policy debates.

The core goal is to ingest, clean, tokenize, and enrich New Zealand legislative and parliamentary texts using a single, memory-efficient pipeline that outputs standardized Apache Parquet tables. By using the same syntactic and semantic layers, cross-referencing between Hansard debates and Legislation is made automatic and mathematically aligned.

## 2. Target Users
- **Policy Researchers & Analysts**: Analyzing legislative trends, citation networks, and political discourse in New Zealand.
- **Data Engineers & Data Scientists**: Looking for a highly optimized, local-first dataset preprocessing pipeline for large-scale legal text.
- **Academic & Independent Researchers**: Performing computational linguistics research on NZ law and parliamentary proceedings without expensive cloud resources.

## 3. Core Features & Architecture
- **Unified Ingestion & Preprocessing**: Streams datasets (e.g. from Hugging Face Datasets Hub) and processes them in parallel chunks via spaCy's `nlp.pipe`.
- **SOTA Māori Language Guard**: 
  - **Bilingual Tokenizer & Subword Preservation**: A customized tokenizer that maps and preserves specific Te Reo Māori words (such as *tikanga*, *taonga*, *kāwanatanga*) as atomic tokens rather than splitting them into English-centric subwords.
  - **Macron Normalization Layer**: Standardizes text to correct unicode representations (NFC normalization) to handle macron variations (`Māori` vs `Maori` vs `Maaori`).
  - **Language and Code-Switching Detection**: Custom patterns and sequence classification to detect and tag Te Reo Māori vs English sections within bilingual texts (e.g. Hansard speeches).
- **Syntactic Layer (spaCy v3)**: Fast sentence segmentation, token cleaning, and custom pattern matching via `EntityRuler` to extract statutory citations (e.g., "Crimes Act 1961") and reference anchors (e.g., "section 4").
- **Semantic Layer (Hugging Face Transformers)**: Local semantic embeddings using quantized (4-bit via `bitsandbytes`) SOTA legal models like `Equall/SaulLM-7B` or `nlpaueb/legal-bert-base-uncased`, leveraging Rust-backed fast tokenizers (`use_fast=True`).
- **Memory-Efficient Local Storage**: Outputting unified datasets to compressed Apache Parquet format.
- **Relational Graphing & Search**: In-memory similarity search using FAISS (without external databases) and relational graph modeling using NetworkX to map connections between parliamentary speeches and enacted laws.
