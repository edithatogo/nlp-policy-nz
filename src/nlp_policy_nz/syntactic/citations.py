"""EntityRuler-based citation patterns for NZ legislation.

Provides spaCy ``EntityRuler`` patterns that match common forms of
New Zealand Act citations (e.g. "Crimes Act 1961") and structural
references (e.g. "section 29", "Part 2", "Schedule 1").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from spacy.pipeline import EntityRuler

if TYPE_CHECKING:
    from spacy.language import Language

# ---------------------------------------------------------------------------
# Entity labels
# ---------------------------------------------------------------------------

CITATION_ENTITY_LABEL: str = "NZ_ACT"
"""Entity label assigned to Act citation spans (e.g. "Crimes Act 1961")."""

SECTION_ENTITY_LABEL: str = "NZ_SECTION"
"""Entity label assigned to structural reference spans (e.g. "section 29")."""

# ---------------------------------------------------------------------------
# EntityRuler patterns
# ---------------------------------------------------------------------------

ACT_PATTERNS: list[dict] = [
    # ── Known NZ Acts ──────────────────────────────────────────────────
    {
        "label": CITATION_ENTITY_LABEL,
        "pattern": [
            {"LOWER": {"IN": ["crimes", "legislation", "māori", "maori"]}},
            {"LOWER": "act"},
            {"SHAPE": "dddd", "LENGTH": 4},
        ],
    },
    # ── Generic "X Act YYYY" ───────────────────────────────────────────
    {
        "label": CITATION_ENTITY_LABEL,
        "pattern": [
            {"IS_TITLE": True, "OP": "+"},
            {"LOWER": "act"},
            {"SHAPE": "dddd", "LENGTH": 4},
        ],
    },
    # ── Section references ─────────────────────────────────────────────
    {
        "label": SECTION_ENTITY_LABEL,
        "pattern": [
            {"LOWER": "section"},
            {"LIKE_NUM": True, "OP": "+"},
        ],
    },
    # ── Part references ────────────────────────────────────────────────
    {
        "label": SECTION_ENTITY_LABEL,
        "pattern": [
            {"LOWER": "part"},
            {"LOWER": {"IN": ["1", "2", "3", "4", "5", "i", "ii", "iii", "iv", "v"]}},
        ],
    },
    # ── Schedule references ────────────────────────────────────────────
    {
        "label": SECTION_ENTITY_LABEL,
        "pattern": [
            {"LOWER": "schedule"},
            {"LIKE_NUM": True, "OP": "+"},
        ],
    },
]
"""EntityRuler pattern definitions for NZ Act and section citation
extraction.

Each dict in this list has a ``"label"`` key (one of
:data:`CITATION_ENTITY_LABEL` or :data:`SECTION_ENTITY_LABEL`) and a
``"pattern"`` key that is a list of token-based attribute dictionaries
suitable for use with spaCy's ``EntityRuler``.
"""


# ---------------------------------------------------------------------------
# Ruler factory
# ---------------------------------------------------------------------------


def create_citation_ruler(nlp: Language) -> EntityRuler:
    """Create and add a citation ``EntityRuler`` to the pipeline.

    Builds an :class:`spacy.pipeline.EntityRuler` configured with all
    patterns from :data:`ACT_PATTERNS` and inserts it into the pipeline
    **after** the ``"maori_guard"`` component.

    Args:
        nlp: A spaCy ``Language`` instance (must already have the
            ``"maori_guard"`` component registered).

    Returns:
        The newly created :class:`spacy.pipeline.EntityRuler` that has
        been added to ``nlp``.

    Raises:
        ValueError: If ``\"maori_guard\"`` is not present in the pipeline.

    Example:
        >>> nlp = create_nlp_pipeline()
        >>> ruler = create_citation_ruler(nlp)
        >>> "citation_ruler" in nlp.pipe_names
        True
    """
    if "maori_guard" not in nlp.pipe_names:
        msg = (
            "Expected 'maori_guard' to be present in the pipeline; "
            "call create_nlp_pipeline() first."
        )
        raise ValueError(msg)

    ruler = nlp.add_pipe(
        "entity_ruler",
        name="citation_ruler",
        after="maori_guard",
        config={"overwrite_ents": True},
    )
    ruler.add_patterns(ACT_PATTERNS)
    return ruler
