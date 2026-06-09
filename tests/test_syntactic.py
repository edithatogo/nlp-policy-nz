"""Tests for the Syntactic Layer (Track 4).

Covers the pipeline factory and the EntityRuler-based citation
pattern matcher.
"""

from __future__ import annotations

import pytest
import spacy
from spacy.language import Language
from spacy.pipeline import EntityRuler

from nlp_policy_nz.syntactic import (
    ACT_PATTERNS,
    CITATION_ENTITY_LABEL,
    PIPELINE_COMPONENTS,
    SECTION_ENTITY_LABEL,
    create_citation_ruler,
    create_nlp_pipeline,
)

# ---------------------------------------------------------------------------
# Pipeline factory tests
# ---------------------------------------------------------------------------


class TestCreateNlpPipeline:
    """Tests for :func:`create_nlp_pipeline`."""

    def test_create_nlp_pipeline_returns_language(self) -> None:
        """Verify that the factory returns a spaCy ``Language`` object."""
        nlp = create_nlp_pipeline()
        assert isinstance(nlp, Language)

    def test_pipeline_has_maori_guard(self) -> None:
        """Check that the ``\"maori_guard\"`` component is in the pipeline."""
        nlp = create_nlp_pipeline()
        assert "maori_guard" in nlp.pipe_names

    def test_pipeline_has_expected_components(self) -> None:
        """Check that expected pipeline components are present."""
        nlp = create_nlp_pipeline()
        for comp in PIPELINE_COMPONENTS:
            assert comp in nlp.pipe_names, f"Missing pipeline component: {comp}"


# ---------------------------------------------------------------------------
# Citation ruler tests
# ---------------------------------------------------------------------------


class TestCreateCitationRuler:
    """Tests for :func:`create_citation_ruler`."""

    @pytest.fixture
    def nlp(self) -> Language:
        """Return a pipeline with the Māori Guard pre-loaded."""
        return create_nlp_pipeline()

    def test_create_citation_ruler_returns_entityruler(self, nlp: Language) -> None:
        """Verify that ``create_citation_ruler`` returns an ``EntityRuler``."""
        ruler = create_citation_ruler(nlp)
        assert isinstance(ruler, EntityRuler)

    def test_create_citation_ruler_adds_pipe(self, nlp: Language) -> None:
        """Verify that the ruler is added to the pipeline after maori_guard."""
        create_citation_ruler(nlp)
        assert "citation_ruler" in nlp.pipe_names
        idx_guard = nlp.pipe_names.index("maori_guard")
        idx_ruler = nlp.pipe_names.index("citation_ruler")
        assert idx_ruler > idx_guard, "citation_ruler must come after maori_guard"

    def test_ruler_raises_without_maori_guard(self) -> None:
        """Calling ``create_citation_ruler`` on a plain pipeline errors."""
        nlp_plain = spacy.load("en_core_web_sm")
        with pytest.raises(ValueError, match="maori_guard"):
            create_citation_ruler(nlp_plain)


# ---------------------------------------------------------------------------
# Pattern matching tests
# ---------------------------------------------------------------------------


class TestActPatterns:
    """Tests for ``ACT_PATTERNS`` against real text."""

    @pytest.fixture
    def nlp(self) -> Language:
        p = create_nlp_pipeline()
        create_citation_ruler(p)
        return p

    def test_act_patterns_crime_example(self, nlp: Language) -> None:
        """'Crimes Act 1961' should be recognised as NZ_ACT."""
        doc = nlp("The Crimes Act 1961 governs criminal law.")
        assert len(doc.ents) >= 1
        nz_acts = [e for e in doc.ents if e.label_ == CITATION_ENTITY_LABEL]
        assert any("Crimes" in e.text and "1961" in e.text for e in nz_acts)

    def test_act_patterns_legislation_example(self, nlp: Language) -> None:
        """'Legislation Act 2019' should be recognised as NZ_ACT."""
        doc = nlp("The Legislation Act 2019 is the key act.")
        nz_acts = [e for e in doc.ents if e.label_ == CITATION_ENTITY_LABEL]
        assert any("Legislation" in e.text and "2019" in e.text for e in nz_acts)

    def test_act_patterns_maori_example(self, nlp: Language) -> None:
        """'Māori Language Act 2016' should be recognised."""
        doc = nlp("Under the Māori Language Act 2016, te reo is official.")
        nz_acts = [e for e in doc.ents if e.label_ == CITATION_ENTITY_LABEL]
        assert any("Māori" in e.text or "Maori" in e.text for e in nz_acts)

    def test_act_patterns_section_ref(self, nlp: Language) -> None:
        """'section 29' should be recognised as NZ_SECTION."""
        doc = nlp("See section 29 of the Act.")
        sections = [e for e in doc.ents if e.label_ == SECTION_ENTITY_LABEL]
        assert any("section" in e.text and "29" in e.text for e in sections)

    def test_act_patterns_part_ref(self, nlp: Language) -> None:
        """'Part 2' should be recognised as NZ_SECTION."""
        doc = nlp("This falls under Part 2.")
        sections = [e for e in doc.ents if e.label_ == SECTION_ENTITY_LABEL]
        assert any("Part" in e.text and "2" in e.text for e in sections)

    def test_act_patterns_schedule_ref(self, nlp: Language) -> None:
        """'Schedule 1' should be recognised as NZ_SECTION."""
        doc = nlp("Refer to Schedule 1 for details.")
        sections = [e for e in doc.ents if e.label_ == SECTION_ENTITY_LABEL]
        assert any("Schedule" in e.text and "1" in e.text for e in sections)


# ---------------------------------------------------------------------------
# Constants / labels tests
# ---------------------------------------------------------------------------


class TestLabels:
    """Sanity checks on the label constants."""

    def test_citation_label_value(self) -> None:
        assert CITATION_ENTITY_LABEL == "NZ_ACT"

    def test_section_label_value(self) -> None:
        assert SECTION_ENTITY_LABEL == "NZ_SECTION"


# ---------------------------------------------------------------------------
# Pattern list structure tests
# ---------------------------------------------------------------------------


class TestActPatternsStructure:
    """Validate that ``ACT_PATTERNS`` has correct shape."""

    def test_patterns_is_list_of_dicts(self) -> None:
        assert isinstance(ACT_PATTERNS, list)
        assert all(isinstance(p, dict) for p in ACT_PATTERNS)

    def test_each_pattern_has_label_and_pattern(self) -> None:
        for p in ACT_PATTERNS:
            assert "label" in p, f"Missing 'label' in pattern: {p}"
            assert "pattern" in p, f"Missing 'pattern' in pattern: {p}"
            assert isinstance(p["pattern"], list)

    def test_all_labels_are_valid(self) -> None:
        valid = {CITATION_ENTITY_LABEL, SECTION_ENTITY_LABEL}
        for p in ACT_PATTERNS:
            assert p["label"] in valid, f"Unexpected label: {p['label']}"
