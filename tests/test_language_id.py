from __future__ import annotations

import pytest
from lingua import IsoCode639_1, Language

from nlp_policy_nz.guard.language_id import (
    LanguageIdentifier,
)


@pytest.fixture(scope="module")
def identifier() -> LanguageIdentifier:
    return LanguageIdentifier()


def test_detect_english(identifier: LanguageIdentifier) -> None:
    result = identifier.detect("This is a simple English sentence.")
    assert result.language == "en"
    assert result.confidence > 0.0
    assert isinstance(result.is_reliable, bool)


def test_detect_maori(identifier: LanguageIdentifier) -> None:
    result = identifier.detect("He waka eke noa.")
    assert result.language == "mi"
    assert result.confidence > 0.0


def test_detect_empty(identifier: LanguageIdentifier) -> None:
    result = identifier.detect("")
    assert result.language == "en"
    assert result.confidence == 0.0
    assert result.is_reliable is False


def test_detect_whitespace(identifier: LanguageIdentifier) -> None:
    result = identifier.detect("   \n\t")
    assert result.language == "en"
    assert result.confidence == 0.0
    assert result.is_reliable is False


def test_detect_sentences(identifier: LanguageIdentifier) -> None:
    sentences = ["This is English.", "He waka eke noa."]
    results = identifier.detect_sentences(sentences)
    assert len(results) == 2
    assert results[0].language == "en"
    assert results[1].language == "mi"


def test_detect_code_switching(identifier: LanguageIdentifier) -> None:
    text = "The meeting will begin shortly. Kia ora koutou katoa."
    segments = identifier.detect_code_switching(text)
    assert len(segments) >= 2

    languages = [lang for lang, seg in segments]
    assert "en" in languages
    assert "mi" in languages

    # Empty and whitespace cases
    assert identifier.detect_code_switching("") == []
    assert identifier.detect_code_switching("   ") == []


def test_to_iso() -> None:
    assert LanguageIdentifier._to_iso(Language.ENGLISH) == "en"
    assert LanguageIdentifier._to_iso(Language.MAORI) == "mi"
    assert LanguageIdentifier._to_iso(None) == "un"

    # Check fallback returns the iso code object or string
    # Depending on what LanguageIdentifier actually returns.
    # The source code returns the attribute directly which is an IsoCode639_1 enum
    assert LanguageIdentifier._to_iso(Language.FRENCH) == IsoCode639_1.FR
