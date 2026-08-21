"""Tests for the Māori Language Guard module (Track 3).

The guard layer is responsible for ensuring that macronised characters
in Te Reo Māori are preserved through the pipeline and that Te Reo
words are not incorrectly split by downstream tokenisers.
"""

from __future__ import annotations

import pytest

from nlp_policy_nz.guard.normalizer import (
    is_macronized,
    normalize_text,
    preserve_macrons,
)

# ---------------------------------------------------------------------------
# Unicode Normalisation Tests
# ---------------------------------------------------------------------------


def test_normalize_text_nfc() -> None:
    """Verify that decomposed Unicode characters are recomposed by NFC
    normalisation.
    """
    # 'a' + COMBINING MACRON (U+0304) -> 'ā' (U+0101)
    decomposed = "Ma\u0304ori"
    result = normalize_text(decomposed)
    assert result == "Māori"
    # Verify the character is actually the composed NFC form.
    assert len(result) == 5  # M, ā, o, r, i  # noqa: PLR2004
    assert "ā" in result


def test_normalize_text_maaori() -> None:
    """Verify that 'Maaori' is corrected to 'Māori' via MACRON_MAP."""
    assert normalize_text("Maaori") == "Māori"
    assert normalize_text("kawanatanga") == "kāwanatanga"


def test_is_macronized_true() -> None:
    """Verify detection of macron characters in Māori words."""
    assert is_macronized("Māori") is True
    assert is_macronized("Whakawā") is True
    assert is_macronized("kāwanatanga") is True
    assert is_macronized("ā") is True
    assert is_macronized("Ā") is True
    assert is_macronized("ēīōū") is True


def test_is_macronized_false() -> None:
    """Verify that plain ASCII text returns False."""
    assert is_macronized("Maori") is False
    assert is_macronized("tikanga") is False
    assert is_macronized("koutou") is False
    assert is_macronized("") is False


def test_preserve_macrons() -> None:
    """Verify that macrons survive a round-trip through preserve_macrons."""
    original = "Māori kāwanatanga Whakawā"
    result = preserve_macrons(original)
    assert result == original
    # Verify NFC form is preserved (no decomposition).
    assert "ā" in result
    assert "ā" in result


# ---------------------------------------------------------------------------
# Language Identifier Tests
# ---------------------------------------------------------------------------

pytest.importorskip("lingua")

from nlp_policy_nz.guard.language_id import (  # noqa: E402
    LANGUAGE_MIIO_CONFIDENCE,
    LanguageIdentifier,
    LanguageResult,
)


def test_language_id_detect_english() -> None:
    """``detect`` returns ``\"en\"`` with high confidence for English text."""
    identifier = LanguageIdentifier()
    result = identifier.detect("The quick brown fox jumps over the lazy dog.")

    assert isinstance(result, LanguageResult)
    assert result.language == "en"
    assert result.confidence >= LANGUAGE_MIIO_CONFIDENCE
    assert result.is_reliable is True


def test_language_id_detect_maori() -> None:
    """``detect`` returns ``\"mi\"`` with high confidence for Te Reo Māori."""
    identifier = LanguageIdentifier()
    result = identifier.detect("Kia ora koutou katoa, e hoa mā.")

    assert isinstance(result, LanguageResult)
    assert result.language == "mi"
    assert result.confidence >= LANGUAGE_MIIO_CONFIDENCE
    assert result.is_reliable is True


def test_language_id_low_confidence() -> None:
    """Very short or ambiguous text produces a low-confidence result."""
    identifier = LanguageIdentifier()
    result = identifier.detect("a")

    assert isinstance(result, LanguageResult)
    # Very short text should yield low confidence.
    assert result.confidence < LANGUAGE_MIIO_CONFIDENCE
    assert result.is_reliable is False


def test_language_id_code_switching() -> None:
    """``detect_code_switching`` splits mixed-language text into segments."""
    identifier = LanguageIdentifier()
    mixed = "Hello world. Kia ora e hoa ma."
    segments = identifier.detect_code_switching(mixed)

    assert isinstance(segments, list)
    assert len(segments) >= 1

    # The concatenation of all segments should reconstruct the original.
    reconstructed = "".join(segment for _, segment in segments)
    assert reconstructed == mixed

    # At least one English segment should be present.
    eng_segments = [s for lang, s in segments if lang == "en"]
    assert len(eng_segments) >= 1
