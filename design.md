# System Design: nlp-policy-nz

## Architecture Overview

```
                        ┌─────────────────────────┐
                        │     CLI (argparse)       │
                        │  nlp-policy-nz <cmd>     │
                        └──────────┬──────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Public API (api.py)                        │
│          process_legislation() / process_hansard()              │
│                       search_similar()                          │
└─────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌───────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│ Māori Guard   │      │  Syntactic Layer    │      │ Semantic Layer   │
│ (guard/)      │◄────►│  (syntactic/)       │      │ (semantic/)      │
│               │      │                     │      │                  │
│ • normalizer  │      │ • pipeline.py       │      │ • model_loader   │
│ • tokenizer   │      │ • citations.py      │      │ • embeddings     │
│ • language_id │      │ • chunking.py       │      │ • finetune       │
└───────┬───────┘      └──────────┬──────────┘      └────────┬─────────┘
        │                        │                          │
        └────────────────────────┼──────────────────────────┘
                                 ▼
                    ┌──────────────────────┐
                    │    Storage Layer     │
                    │    (storage/)        │
                    │                      │
                    │ • serialization.py   │
                    │ • vectordb.py        │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
            ┌──────────────┐     ┌──────────────────┐
            │  Parquet     │     │  LanceDB         │
            │  (PyArrow)   │     │  (Vector Index)  │
            └──────────────┘     └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Integration Layer                           │
│                     (integrations/)                             │
│ • huggingface.py    — Dataset loading from HF Hub              │
│ • hf_uploader.py    — Dataset uploading to HF Hub              │
│ • dataset_card.py   — Auto-generated dataset cards             │
│ • zenodo.py         — Zenodo API client (sandbox + production) │
│ • zenodo_archive.py — Archive & release workflow               │
│ • release.py        — ReleaseManager for versioned archives    │
│ • data_registry.py  — DataSovereigntyRegistry for provenance   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     API Server (api/)                           │
│ • server.py — FastAPI app with /health, /embed, /search,       │
│               /process endpoints. Lazy-loads heavy deps.        │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Legislation Pipeline
```
XML/HTML Input → Universal Ingestion Engine → Māori Guard →
Syntactic Parsing → Citation Extraction → Chunking →
(Optional: Semantic Embeddings) → Parquet Serialization
```

### Hansard Pipeline
```
JSONL/Text Input → Universal Ingestion Engine → Māori Guard →
Syntactic Parsing → Code-Switching Detection → Chunking →
(Optional: Semantic Embeddings) → Parquet Serialization
```

## Module Responsibilities

### guard/
- **normalizer.py**: NFC unicode normalization, macron variant reduction
- **tokenizer_exceptions.py**: spaCy tokenizer rules preserving Te Reo Māori lexical atoms
- **language_id.py**: Language detection and code-switching identification (mi/en)

### syntactic/
- **pipeline.py**: spaCy pipeline factory integrating Māori Guard component
- **citations.py**: EntityRuler patterns for NZ Act/Section cross-references
- **chunking.py**: Sentence-level document chunking with doc_id generation

### semantic/
- **model_loader.py**: Quantized model loading (4-bit/8-bit/none) with fallback support
- **embeddings.py**: Dense embedding generation with mean pooling
- **finetune.py**: MLM fine-tuning orchestration for domain adaptation

### storage/
- **serialization.py**: Parquet read/write via narwhals + PyArrow
- **vectordb.py**: LanceDB vector index creation, search, and management

### integrations/
- **huggingface.py**: Dataset loading from Hugging Face Hub
- **hf_uploader.py**: Dataset uploading to Hugging Face Hub with metadata cards
- **dataset_card.py**: Auto-generated YAML + markdown dataset cards
- **zenodo.py**: Zenodo API deposit client (sandbox + production)
- **zenodo_archive.py**: Archive creation and publishing workflow
- **release.py**: ReleaseManager for versioned archives
- **data_registry.py**: DataSovereigntyRegistry for provenance

### cli/
- **main.py**: argparse CLI with process, search, upload-dataset, deploy-space, archive-to-zenodo, release commands
- **graph.py**: NetworkX-based relational graph for cross-referencing

### api/
- **server.py**: FastAPI inference server with lazy-loaded dependencies

## Versioning Strategy

- **v1** (`universal_framework_v1.py`): Baseline ingestion and schema emission
- **v2** (`universal_framework_v2.py`): Maximum-standards (TEI sentence tags, AKN metadata, dependency index JSONL)
- **v3** (`universal_framework_v3.py`): Further enhanced ingestion with additional XML structural support

All versions are preserved and never overwritten.

## Downstream Consumers

```
nlp-policy-nz (this repo)
    │
    ├──► corpus-law-nz (Legal NLP)
    │       • Statutory hierarchy extraction
    │       • Citation network analysis
    │       • Binding obligation detection ("must", "shall")
    │
    └──► corpus-nz-hansard (Parliamentary NLP)
            • Speaker-to-party mapping
            • Political sentiment analysis
            • Policy debate tracking
```
