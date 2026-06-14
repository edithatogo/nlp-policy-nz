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

__all__ = [
    "DeonticModality",
    "DeonticModalityDetector",
    "LegalEffect",
    "ModalityAnnotation",
    "classify_legal_effect",
    "detect_modality",
]
