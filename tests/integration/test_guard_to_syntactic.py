"""Integration tests from Māori guard normalisation to syntactic citation rules."""

from __future__ import annotations

import spacy

from nlp_policy_nz.guard import create_maori_guard_component, normalize_text
from nlp_policy_nz.syntactic import CITATION_ENTITY_LABEL, create_citation_ruler


def test_guard_normalized_text_flows_into_citation_ruler() -> None:
    """Macron-normalised text remains compatible with syntactic citation extraction."""
    nlp = spacy.blank("en")
    create_maori_guard_component(nlp)
    create_citation_ruler(nlp)
    text = normalize_text("The Maaori Act 2024 protects tikanga Maaori.")

    doc = nlp(text)
    citations = [(entity.text, entity.label_) for entity in doc.ents]

    assert "Māori" in text
    assert ("Māori Act 2024", CITATION_ENTITY_LABEL) in citations
