"""Tests for Track 10 legal effect classification.

Test classes mirror the structure of :mod:`test_feature_extraction` and cover
the :class:`LegalEffect` enum, modality-based classification, regex-based
classification, and edge cases.
"""

from __future__ import annotations

import pytest
import spacy

from nlp_policy_nz.legal.effects import LegalEffect, classify_legal_effect

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def nlp() -> spacy.Language:
    """Build an ``en_core_web_sm`` pipeline with the deontic modality component."""
    _nlp = spacy.load("en_core_web_sm")
    _nlp.add_pipe("deontic_modality", after="parser")
    return _nlp


# ---------------------------------------------------------------------------
# LegalEffect Enum Tests
# ---------------------------------------------------------------------------


class TestLegalEffectEnum:
    """Tests for the :class:`LegalEffect` enum."""

    def test_enum_values(self) -> None:
        """Verify all 7 enum members are present with expected values."""
        expected = {
            LegalEffect.OBLIGATION: "obligation",
            LegalEffect.PROHIBITION: "prohibition",
            LegalEffect.PERMISSION: "permission",
            LegalEffect.POWER: "power",
            LegalEffect.LIABILITY: "liability",
            LegalEffect.IMMUNITY: "immunity",
            LegalEffect.DISABILITY: "disability",
        }
        assert len(LegalEffect) == 7
        for member, expected_value in expected.items():
            assert member.value == expected_value

    def test_enum_str(self) -> None:
        """``__str__`` returns the value string."""
        assert str(LegalEffect.OBLIGATION) == "obligation"
        assert str(LegalEffect.PROHIBITION) == "prohibition"
        assert str(LegalEffect.PERMISSION) == "permission"
        assert str(LegalEffect.POWER) == "power"
        assert str(LegalEffect.LIABILITY) == "liability"
        assert str(LegalEffect.IMMUNITY) == "immunity"
        assert str(LegalEffect.DISABILITY) == "disability"

    def test_enum_from_value(self) -> None:
        """``LegalEffect(value)`` constructs the correct member."""
        assert LegalEffect("obligation") is LegalEffect.OBLIGATION
        assert LegalEffect("prohibition") is LegalEffect.PROHIBITION
        assert LegalEffect("permission") is LegalEffect.PERMISSION
        assert LegalEffect("power") is LegalEffect.POWER
        assert LegalEffect("liability") is LegalEffect.LIABILITY
        assert LegalEffect("immunity") is LegalEffect.IMMUNITY
        assert LegalEffect("disability") is LegalEffect.DISABILITY


# ---------------------------------------------------------------------------
# Modality-Based Classification Tests
# ---------------------------------------------------------------------------


class TestClassifyLegalEffectFromModalities:
    """Tests for :func:`classify_legal_effect` using the spaCy pipeline."""

    def test_obligation_from_modalities(self, nlp: spacy.Language) -> None:
        """``must`` text is classified as OBLIGATION."""
        result = classify_legal_effect("The chief executive must keep a register.", nlp)
        assert result == "obligation"

    def test_prohibition_from_modalities(self, nlp: spacy.Language) -> None:
        """``must not`` text is classified as PROHIBITION."""
        result = classify_legal_effect("A person must not disclose protected information.", nlp)
        assert result == "prohibition"

    def test_permission_from_modalities(self, nlp: spacy.Language) -> None:
        """``may`` text is classified as PERMISSION."""
        result = classify_legal_effect("The Minister may approve the amendment.", nlp)
        assert result == "permission"

    def test_priority_cascade(self, nlp: spacy.Language) -> None:
        """When multiple modalities exist, PROHIBITION wins (highest priority)."""
        result = classify_legal_effect(
            "The Minister must appoint a committee. "
            "An officer shall not interfere with the process.",
            nlp,
        )
        assert result == "prohibition"

    def test_multiple_modalities_selects_highest_priority(self, nlp: spacy.Language) -> None:
        """With three modalities, pick the highest-priority one (PROHIBITION)."""
        result = classify_legal_effect(
            "The applicant may submit evidence. "
            "The officer must verify it. "
            "The board shall not reject without cause.",
            nlp,
        )
        assert result == "prohibition"

    def test_empty_modalities_list(self, nlp: spacy.Language) -> None:
        """When the pipeline finds no modalities, it falls back to regex."""
        result = classify_legal_effect("The is liable for damages.", nlp)
        assert result == "liability"

    def test_modalities_none(self) -> None:
        """When ``nlp=None``, the function falls back to regex only."""
        result = classify_legal_effect("The applicant must provide evidence.", nlp=None)
        assert result == "obligation"


# ---------------------------------------------------------------------------
# Regex-Based Classification Tests
# ---------------------------------------------------------------------------


class TestClassifyLegalEffectRegex:
    """Tests for :func:`classify_legal_effect` regex fallback."""

    def test_must_obligation(self) -> None:
        """``must`` triggers OBLIGATION via regex fallback."""
        result = classify_legal_effect("The applicant must provide", nlp=None)
        assert result == "obligation"

    def test_shall_obligation(self) -> None:
        """``shall`` triggers OBLIGATION via regex fallback."""
        result = classify_legal_effect("The Minister shall appoint", nlp=None)
        assert result == "obligation"

    def test_must_not_prohibition(self) -> None:
        """``must not`` triggers PROHIBITION via regex fallback."""
        result = classify_legal_effect("A person must not", nlp=None)
        assert result == "prohibition"

    def test_shall_not_prohibition(self) -> None:
        """``shall not`` triggers PROHIBITION via regex fallback."""
        result = classify_legal_effect("shall not", nlp=None)
        assert result == "prohibition"

    def test_may_permission(self) -> None:
        """``may`` triggers PERMISSION via regex fallback."""
        result = classify_legal_effect("may apply", nlp=None)
        assert result == "permission"

    def test_power_has_the_power(self) -> None:
        """``has power`` triggers POWER."""
        result = classify_legal_effect("has the power to", nlp=None)
        assert result == "power"

    def test_power_may_by_notice(self) -> None:
        """``may`` alone triggers PERMISSION, but POWER marker takes priority."""
        result = classify_legal_effect("may make regulations", nlp=None)
        assert result == "power"

    def test_liability(self) -> None:
        """``is liable`` triggers LIABILITY."""
        result = classify_legal_effect("is liable", nlp=None)
        assert result == "liability"

    def test_liability_offence(self) -> None:
        """``commits an offence`` triggers LIABILITY."""
        result = classify_legal_effect("commits an offence", nlp=None)
        assert result == "liability"

    def test_immunity(self) -> None:
        """``is immune from`` triggers IMMUNITY."""
        result = classify_legal_effect("is immune from", nlp=None)
        assert result == "immunity"

    def test_disability(self) -> None:
        """``is disqualified`` triggers DISABILITY."""
        result = classify_legal_effect("is disqualified", nlp=None)
        assert result == "disability"

    def test_disability_not_eligible(self) -> None:
        """``not eligible`` triggers DISABILITY."""
        result = classify_legal_effect("not eligible", nlp=None)
        assert result == "disability"


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestClassifyLegalEffectEdgeCases:
    """Tests for edge cases of :func:`classify_legal_effect`."""

    def test_empty_text(self) -> None:
        """Empty string returns ``None``."""
        result = classify_legal_effect("", nlp=None)
        assert result is None

    def test_no_match_default(self) -> None:
        """Text with no detectable modality returns ``None``."""
        result = classify_legal_effect("The committee met on Monday.", nlp=None)
        assert result is None

    def test_case_insensitivity(self) -> None:
        """``MUST`` capitalised is still classified as OBLIGATION."""
        result = classify_legal_effect("MUST", nlp=None)
        assert result == "obligation"

    def test_multiple_sentences(self) -> None:
        """Multiple sentences with modality in first sentence are classified."""
        result = classify_legal_effect(
            "The committee met on Monday. The Minister shall publish the report.",
            nlp=None,
        )
        assert result == "obligation"


# ---------------------------------------------------------------------------
# Module-Level Function Export
# ---------------------------------------------------------------------------


def test_classify_legal_effect_module_level() -> None:
    """``classify_legal_effect`` is exported and callable from the module."""
    assert callable(classify_legal_effect)
    result = classify_legal_effect("The applicant must provide", nlp=None)
    assert result == "obligation"
