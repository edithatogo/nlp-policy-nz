"""Tests for the Māori Language Guard module (Track 3).

The guard layer is responsible for ensuring that macronised characters
in Te Reo Māori are preserved through the pipeline and that Te Reo
words are not incorrectly split by downstream tokenisers.
"""

from __future__ import annotations

import spacy
import pytest
from spacy import util as spacy_util

from nlp_policy_nz.guard.normalizer import (
    is_macronized,
    normalize_text,
    preserve_macrons,
)
from nlp_policy_nz.guard.tokenizer_exceptions import (
    TE_REO_LEXICAL_ATOM_SET,
    build_tokenizer_exceptions,
    create_maori_guard_component,
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
# Tokenizer Exception Tests
# ---------------------------------------------------------------------------


class TestTeReoLexicalAtomSet:
    """Test suite for :data:`TE_REO_LEXICAL_ATOM_SET`."""

    _KEY_WORDS: tuple[str, ...] = (
        "tikanga",
        "taonga",
        "kāwanatanga",
        "Whakawā",
        "koutou",
        "Māori",
        "Pākehā",
        "Aotearoa",
        "whānau",
        "hapū",
        "iwi",
        "rohe",
        "kōrero",
        "whakapapa",
        "wānanga",
        "mana",
        "tapu",
        "noa",
        "utu",
        "koha",
        "aroha",
        "whakaminenga",
        "tiriti",
        "rangatiratanga",
        "motuhake",
        "whakahaere",
        "pūtea",
    )

    def test_te_reo_lexical_atom_set_contains_key_words(self) -> None:
        """Check that important Te Reo words are present in the atom set."""
        missing = [w for w in self._KEY_WORDS if w not in TE_REO_LEXICAL_ATOM_SET]
        assert not missing, f"Missing atoms: {missing}"

    def test_te_reo_lexical_atom_set_has_at_least_twenty_items(self) -> None:
        """The set should contain at least 20 entries."""
        assert len(TE_REO_LEXICAL_ATOM_SET) >= 20  # noqa: PLR2004

    def test_te_reo_lexical_atom_set_is_frozenset_of_strings(self) -> None:
        """Verify the type of the exported constant."""
        assert isinstance(TE_REO_LEXICAL_ATOM_SET, frozenset)
        assert all(isinstance(w, str) for w in TE_REO_LEXICAL_ATOM_SET)


class TestBuildTokenizerExceptions:
    """Test suite for :func:`build_tokenizer_exceptions`."""

    def test_build_tokenizer_exceptions_returns_dict(self) -> None:
        """Verify the return type of the builder."""
        result = build_tokenizer_exceptions()
        assert isinstance(result, dict)

    def test_build_tokenizer_exceptions_covers_all_atoms(self) -> None:
        """Every atom in the set should have an exception rule."""
        result = build_tokenizer_exceptions()
        for atom in TE_REO_LEXICAL_ATOM_SET:
            assert atom in result, f"Missing exception for {atom!r}"

    def test_build_tokenizer_exceptions_orth_format(self) -> None:
        """Each rule should be a list containing a dict with an ORTH key."""
        result = build_tokenizer_exceptions()
        for atom, rules in result.items():
            assert isinstance(rules, list), f"Rules for {atom!r} is not a list"
            assert len(rules) == 1, f"Expected exactly one rule for {atom!r}"
            rule = rules[0]
            assert isinstance(rule, dict), f"Rule for {atom!r} is not a dict"
            assert spacy_util.ORTH in rule, f"Rule for {atom!r} missing ORTH key"
            assert rule[spacy_util.ORTH] == atom, f"Rule ORTH does not match atom {atom!r}"

    def test_build_tokenizer_exceptions_empty_is_false(self) -> None:
        """The returned dict should not be empty."""
        result = build_tokenizer_exceptions()
        assert result, "Exception dict should not be empty"


class TestCreateMaoriGuardComponent:
    """Test suite for :func:`create_maori_guard_component`."""

    def test_create_maori_guard_component_is_callable(self) -> None:
        """The factory should return a callable."""
        nlp = spacy.blank("en")
        component = create_maori_guard_component(nlp)
        assert callable(component)

    def test_create_maori_guard_updates_tokenizer_rules(self) -> None:
        """Calling the factory should merge atoms into the tokeniser rules."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        for atom in TE_REO_LEXICAL_ATOM_SET:
            assert atom in nlp.tokenizer.rules, f"Missing rule for {atom!r}"

    def test_create_maori_guard_adds_pipe(self) -> None:
        """The ``maori_guard`` component should be in the pipeline."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        assert "maori_guard" in nlp.pipe_names

    def test_create_maori_guard_pipe_is_first(self) -> None:
        """The guard component should be the first in the pipeline."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        assert nlp.pipe_names[0] == "maori_guard"

    def test_create_maori_guard_double_call_is_idempotent(self) -> None:
        """Calling the factory twice should not duplicate the component."""
        nlp = spacy.blank("en")
        _ = create_maori_guard_component(nlp)
        _ = create_maori_guard_component(nlp)
        assert nlp.pipe_names.count("maori_guard") == 1


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
