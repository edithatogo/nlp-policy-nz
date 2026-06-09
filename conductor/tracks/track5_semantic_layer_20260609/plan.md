# Plan: Track 5 Semantic Layer & Quantized Embeddings

This track integrates Hugging Face transformer models with 4-bit quantization for local embedding generation.

---

### [ ] Task 5.1: Integrate Local LLM Loader
- **Action**: Implement quantized 4-bit loading via bitsandbytes for SaulLM-7B/Legal-BERT.
- **Why**: Enables local, memory-efficient semantic embeddings.

### [ ] Task 5.2: Implement Embedding Generators
- **Action**: Code dense vector generation pipelines using Hugging Face fast tokenizers, releasing Python GIL.
- **Why**: Produces standardized embeddings for the pipeline output schema.

---
