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
from nlp_policy_nz.semantic.vllm_runtime import (
    Track62BenchmarkRow,
    Track62EvidenceReport,
    VLLMGenerationResult,
    VLLMRuntimeError,
    build_track62_evidence_report,
    compare_track62_runtime_to_baseline,
    generate_completion_via_openai_endpoint,
    generate_completion_via_vllm,
    render_track62_evidence_markdown,
)

__all__: list[str] = [
    "DEFAULT_MODEL",
    "DEFAULT_QUANTIZATION",
    "FALLBACK_MODEL",
    "EmbeddingGenerator",
    "EmbeddingResult",
    "ModelLoadError",
    "QuantizationConfig",
    "Track62BenchmarkRow",
    "Track62EvidenceReport",
    "VLLMGenerationResult",
    "VLLMRuntimeError",
    "build_track62_evidence_report",
    "compare_track62_runtime_to_baseline",
    "generate_completion_via_openai_endpoint",
    "generate_completion_via_vllm",
    "generate_embedding",
    "generate_embeddings_batch",
    "load_model",
    "render_track62_evidence_markdown",
    "unload_model",
]
