"""Pipeline loader for the NLP Policy NZ syntactic layer.

Provides a factory function that builds a spaCy ``Language`` pipeline
with the Māori Guard tokeniser component pre-registered, ready for
EntityRuler-based citation matching.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import spacy
from spacy.language import Language

from nlp_policy_nz.guard import create_maori_guard_component

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIPELINE_COMPONENTS: list[str] = [
    "tok2vec",
    "tagger",
    "parser",
    "ner",
    "attribute_ruler",
    "lemmatizer",
    "maori_guard",
]
"""Expected pipeline component names after calling :func:`create_nlp_pipeline`."""


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_nlp_pipeline(model: str = "en_core_web_sm") -> Language:
    """Create and return a spaCy pipeline with Māori Guard integration.

    Loads the specified spaCy model, registers the ``"maori_guard"``
    pipeline component (including tokeniser exceptions for te reo Māori
    lexical atoms), and returns the configured ``Language`` object.

    Args:
        model: Name of the spaCy model to load (e.g. ``"en_core_web_sm"``).

    Returns:
        A :class:`spacy.language.Language` pipeline with the Māori Guard
        component attached.

    Example:
        >>> nlp = create_nlp_pipeline()
        >>> "maori_guard" in nlp.pipe_names
        True
    """
    nlp: Language = spacy.load(model)
    create_maori_guard_component(nlp)
    return nlp
