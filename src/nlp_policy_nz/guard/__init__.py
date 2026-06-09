"""
Māori Language Guard Module.

Validates and enforces correct Māori language usage and orthographic conventions
within the NLP preprocessing pipeline for New Zealand legislative and parliamentary texts.
"""

from __future__ import annotations

from nlp_policy_nz.guard.language_id import LanguageIdentifier, LanguageResult
from nlp_policy_nz.guard.normalizer import (
    MACRON_MAP,
    is_macronized,
    normalize_text,
    preserve_macrons,
)
from nlp_policy_nz.guard.tokenizer_exceptions import (
    TE_REO_LEXICAL_ATOM_SET,
    TE_REO_PREFIXES,
    build_tokenizer_exceptions,
    create_maori_guard_component,
)

__all__: list[str] = [
    "LanguageIdentifier",
    "LanguageResult",
    "normalize_text",
    "is_macronized",
    "preserve_macrons",
    "MACRON_MAP",
    "TE_REO_LEXICAL_ATOM_SET",
    "TE_REO_PREFIXES",
    "build_tokenizer_exceptions",
    "create_maori_guard_component",
]
