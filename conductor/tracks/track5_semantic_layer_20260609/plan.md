# Plan: Track 5 Semantic Layer & Quantized Embeddings [b65c685]

This track integrates Hugging Face transformer models with 4-bit quantization for local embedding generation.

---

### [x] Task 5.1: Integrate Local LLM Loader
- **Action**: Implement quantized 4-bit loading via bitsandbytes for SaulLM-7B/Legal-BERT.
- **Why**: Enables local, memory-efficient semantic embeddings.
- **Completed**: Created `semantic/model_loader.py` with `load_model()` supporting 4-bit/8-bit/none quantization, `QuantizationConfig` (msgspec Struct), `ModelLoadError`, `unload_model()`, and fallback model support (`nlpaueb/legal-bert-base-uncased` → `bert-base-uncased`).

### [x] Task 5.2: Implement Embedding Generators
- **Action**: Code dense vector generation pipelines using Hugging Face fast tokenizers, releasing Python GIL.
- **Why**: Produces standardized embeddings for the pipeline output schema.
- **Completed**: Created `semantic/embeddings.py` with `generate_embedding()`, `generate_embeddings_batch()`, `_mean_pooling()`, and `EmbeddingGenerator` context manager class with `embed()` and `embed_batch()` methods. Uses `use_fast=True` for fast Rust-backed tokenizers.

---
