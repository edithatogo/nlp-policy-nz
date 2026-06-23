"""Property-based tests for text normalisation boundaries."""

from __future__ import annotations

import unicodedata

from hypothesis import given
from hypothesis import strategies as st

from nlp_policy_nz.guard import normalize_text, preserve_macrons


@given(st.text())
def test_preserve_macrons_always_returns_nfc(text: str) -> None:
    """Macron preservation always returns NFC-normalised text."""
    result = preserve_macrons(text)

    assert unicodedata.is_normalized("NFC", result)


@given(st.sampled_from(["Maaori", "kawanatanga", "whanau", "Pakeha"]))
def test_known_maori_variants_normalise_to_macron_forms(text: str) -> None:
    """Known Māori spelling variants are normalised to macron forms."""
    result = normalize_text(text)

    assert any(char in result for char in "āēīōūĀĒĪŌŪ")
