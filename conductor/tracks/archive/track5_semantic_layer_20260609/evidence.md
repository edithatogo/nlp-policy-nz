# Track 5 Evidence - Semantic Layer and Quantized Embeddings

Track 5 is complete for repo-side semantic model-loading and embedding scaffolding.

Implemented surfaces:

- `src/nlp_policy_nz/semantic/model_loader.py` provides Hugging Face tokenizer/model loading, quantization configuration, fallback model behavior, and model unload helpers.
- `src/nlp_policy_nz/semantic/embeddings.py` provides mean-pooling embedding generation, batch embedding generation, `EmbeddingResult`, and `EmbeddingGenerator`.
- `src/nlp_policy_nz/semantic/__init__.py` exposes the stable semantic API.

Validation evidence:

- `tests/test_semantic.py` covers default/fallback model constants, quantization config behavior, 4-bit/8-bit/unquantized config paths, fallback loading, error handling, dtype selection, and unload behavior.
- `tests/test_embeddings.py` covers embedding result shape, function signatures, context manager behavior, and embedding generator API contracts.
- The Track 5 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Live Hugging Face model downloads and GPU execution require explicit operator intent and are outside this offline repo-side track.
- Model quality and runtime benchmark claims belong to later evaluation and fine-tuning tracks.
