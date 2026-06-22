"""Legal Analysis Layer.

Provides deontic modality detection and legal effect classification mapping to LKIF categories.
"""

from nlp_policy_nz.legal.effects import LegalEffect, classify_legal_effect
from nlp_policy_nz.legal.modality import (
    DeonticModality,
    DeonticModalityDetector,
    ModalityAnnotation,
    detect_modality,
)
from nlp_policy_nz.legal.temporal import (
    TEMPORAL_PATTERNS,
    TemporalExpression,
    TemporalExtractor,
    TemporalGraph,
    TemporalType,
    detect_temporal_expressions,
)

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
