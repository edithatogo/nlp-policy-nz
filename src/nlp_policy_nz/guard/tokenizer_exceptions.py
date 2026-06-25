"""spaCy tokenizer exception rules for Te Reo Māori.

Provides a set of lexical atoms that must be preserved as single tokens
during spaCy tokenisation, along with a factory function for a pipeline
component that pre-processes text to protect these terms.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

import spacy
from spacy import util as spacy_util
from spacy.language import Language

if TYPE_CHECKING:
    from collections.abc import Callable

# ---------------------------------------------------------------------------
# Lexical Atom Set
# ---------------------------------------------------------------------------

TE_REO_LEXICAL_ATOM_SET: frozenset[str] = frozenset(
    {
        # Treaty / governance terms
        "tikanga",
        "taonga",
        "kāwanatanga",
        "Whakawā",
        "rangatiratanga",
        "motuhake",
        "whakahaere",
        "pūtea",
        "whakaminenga",
        "tiriti",
        # People / collective nouns
        "Māori",
        "Pākehā",
        "Aotearoa",
        "whānau",
        "hapū",
        "iwi",
        "rohe",
        # Cultural concepts
        "kōrero",
        "whakapapa",
        "wānanga",
        "mana",
        "tapu",
        "noa",
        "utu",
        "koha",
        "aroha",
        # Pronouns / function words
        "koutou",
    }
)

# ---------------------------------------------------------------------------
# Prefixes
# ---------------------------------------------------------------------------

TE_REO_PREFIXES: list[str] = [
    "te",
    "ngā",
    "nga",
    "tōku",
    "tōu",
    "tana",
    "ōku",
    "ōu",
    "ana",
    "he",
    "ki",
    "kei",
    "i",
    "o",
    "a",
    "e",
    "ko",
    "ka",
    "kua",
    "me",
    "mai",
    "atu",
    "rawa",
    "tonu",
    "ano",
    "kē",
    "rā",
    "nei",
    "nā",
    "nō",
]

# ---------------------------------------------------------------------------
# Exception builder
# ---------------------------------------------------------------------------


def build_tokenizer_exceptions() -> dict[str, list[dict[str, Any]]]:
    """Build spaCy-compatible tokenizer exception rules for Te Reo Māori atoms.

    Each word in :data:`TE_REO_LEXICAL_ATOM_SET` is given a single-token
    orth rule that prevents spaCy from splitting it on internal hyphens,
    apostrophes, or other subword boundaries.

    Returns:
        A dictionary mapping each atom to a list containing one ``ORTH`` rule,
        ready to be merged with ``nlp.tokenizer.rules``.

    """
    exceptions: dict[str, list[dict[str, Any]]] = {}
    for word in TE_REO_LEXICAL_ATOM_SET:
        exceptions[word] = [{spacy_util.ORTH: word}]
    return exceptions


# ---------------------------------------------------------------------------
# Guard pipeline component factory
# ---------------------------------------------------------------------------


@Language.component("maori_guard")
def _maori_guard_component(doc: spacy.tokens.Doc) -> spacy.tokens.Doc:
    """Pipeline component that returns the document unchanged.

    The actual protection of Te Reo lexical atoms is handled at the
    tokeniser level via :func:`build_tokenizer_exceptions`.  This component
    is registered as a no-op hook so that downstream consumers can depend on
    its presence in the pipeline.

    Args:
        doc: A spaCy ``Doc`` produced by the tokeniser.

    Returns:
        The same ``Doc``, passed through unmodified.

    """
    return doc


def create_maori_guard_component(
    nlp: Language,
) -> Callable[[spacy.tokens.Doc], spacy.tokens.Doc]:
    """Register tokeniser exceptions and return the guard component.

    This function:
    1. Builds orth exceptions from :data:`TE_REO_LEXICAL_ATOM_SET`.
    2. Merges them into ``nlp.tokenizer.rules``.
    3. Adds the ``"maori_guard"`` pipeline component (if not already present).

    The returned callable is the guard component itself and can be used
    directly in a custom pipeline.

    Args:
        nlp: A spaCy ``Language`` instance whose tokeniser rules will be
            updated.

    Returns:
        The ``"maori_guard"`` pipeline component (a no-op function that
        accepts and returns a ``Doc``).

    """
    # Merge tokenizer exceptions into the pipeline's tokeniser rules.
    exceptions = build_tokenizer_exceptions()
    nlp.tokenizer.rules.update(exceptions)

    # Add the guard component to the pipeline as the first step so that it
    # runs before any downstream processing.
    if "maori_guard" not in nlp.pipe_names:
        nlp.add_pipe("maori_guard", first=True)

    return _maori_guard_component
