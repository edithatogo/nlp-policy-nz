"""
Syntactic Layer Module.

Provides dependency parsing, constituency parsing, and part-of-speech tagging
capabilities for the NLP pipeline, leveraging spaCy and transformer-based models.
"""

from nlp_policy_nz.syntactic.chunking import (
    chunk_by_sentence,
    chunk_hansard_speech,
    chunk_legislation_document,
    generate_hansard_id,
    generate_legislation_id,
)
from nlp_policy_nz.syntactic.citations import (
    ACT_PATTERNS,
    CITATION_ENTITY_LABEL,
    SECTION_ENTITY_LABEL,
    create_citation_ruler,
)
from nlp_policy_nz.syntactic.pipeline import PIPELINE_COMPONENTS, create_nlp_pipeline

__all__: list[str] = [
    "ACT_PATTERNS",
    "CITATION_ENTITY_LABEL",
    "SECTION_ENTITY_LABEL",
    "chunk_by_sentence",
    "chunk_hansard_speech",
    "chunk_legislation_document",
    "create_citation_ruler",
    "create_nlp_pipeline",
    "generate_hansard_id",
    "generate_legislation_id",
    "PIPELINE_COMPONENTS",
]
