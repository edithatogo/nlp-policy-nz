"""Legal Analysis Layer.

Provides deontic modality detection and legal effect classification mapping to LKIF categories.
"""

from __future__ import annotations

__all__ = [
    "TEMPORAL_PATTERNS",
    "DeonticModality",
    "DeonticModalityDetector",
    "LegalEffect",
    "ModalityAnnotation",
    "TemporalExpression",
    "TemporalExtractor",
    "TemporalGraph",
    "TemporalType",
    "classify_legal_effect",
    "detect_modality",
    "detect_temporal_expressions",
]


def __getattr__(name: str) -> object:
    """Lazily resolve legal analysis helpers."""
    if name in {"LegalEffect", "classify_legal_effect"}:
        module = __import__("nlp_policy_nz.legal.effects", fromlist=[name])
        return getattr(module, name)
    if name in {
        "DeonticModality",
        "DeonticModalityDetector",
        "ModalityAnnotation",
        "detect_modality",
    }:
        module = __import__("nlp_policy_nz.legal.modality", fromlist=[name])
        return getattr(module, name)
    if name in {
        "TEMPORAL_PATTERNS",
        "TemporalExpression",
        "TemporalExtractor",
        "TemporalGraph",
        "TemporalType",
        "detect_temporal_expressions",
    }:
        module = __import__("nlp_policy_nz.legal.temporal", fromlist=[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
