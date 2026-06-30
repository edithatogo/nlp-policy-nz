"""
Semantic Layer Module.

Implements semantic analysis including entity recognition, relation extraction,
and embedding-based semantic search for legislative and parliamentary content.
"""

from __future__ import annotations

from nlp_policy_nz.semantic.embeddings import (
    EmbeddingGenerator,
    EmbeddingResult,
    generate_embedding,
    generate_embeddings_batch,
)
from nlp_policy_nz.semantic.model_loader import (
    DEFAULT_MODEL,
    DEFAULT_QUANTIZATION,
    FALLBACK_MODEL,
    ModelLoadError,
    QuantizationConfig,
    load_model,
    unload_model,
)

__all__: list[str] = [
    "DEFAULT_MODEL",
    "DEFAULT_QUANTIZATION",
    "FALLBACK_MODEL",
    "EmbeddingGenerator",
    "EmbeddingResult",
    "ModelLoadError",
    "QuantizationConfig",
    "generate_embedding",
    "generate_embeddings_batch",
    "load_model",
    "unload_model",
]
