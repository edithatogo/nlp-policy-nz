"""Tests for the Document Chunking module (Task 4.3).

Covers ID generation for legislation and Hansard chunks as well as
sentence-level segmentation via spaCy.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import spacy

from nlp_policy_nz.syntactic.chunking import (
    chunk_by_sentence,
    chunk_hansard_speech,
    chunk_legislation_document,
    generate_hansard_id,
    generate_legislation_id,
)

if TYPE_CHECKING:
    from spacy.language import Language

# ---------------------------------------------------------------------------
# ID Generation
# ---------------------------------------------------------------------------


class TestGenerateLegislationId:
    """Tests for :func:`generate_legislation_id`."""

    def test_generate_legislation_id_format(self) -> None:
        """Verify the returned ID matches pattern."""
        result = generate_legislation_id(1961, 43, 4)
        assert result == "NZ-ACT-1961-043-SEC-4"

    def test_generate_legislation_id_zero_padded(self) -> None:
        """Act numbers below 100 should be zero-padded to three digits."""
        result = generate_legislation_id(2024, 7, 12)
        assert result == "NZ-ACT-2024-007-SEC-12"

    def test_generate_legislation_id_str_section(self) -> None:
        """Section may be passed as a string."""
        result = generate_legislation_id(2024, 1, "4A")
        assert result == "NZ-ACT-2024-001-SEC-4A"

    def test_generate_legislation_id_matches_pattern(self) -> None:
        """Verify the general pattern: NZ-ACT-\\d{4}-\\d{3}-SEC-.+"""
        result = generate_legislation_id(2023, 99, 1)
        assert re.fullmatch(r"NZ-ACT-\d{4}-\d{3}-SEC-.+", result)


class TestGenerateHansardId:
    """Tests for :func:`generate_hansard_id`."""

    def test_generate_hansard_id_format(self) -> None:
        """Verify the returned ID matches pattern."""
        result = generate_hansard_id("2023-05-12", 4)
        assert result == "NZ-HANS-2023-05-12-SP-04"

    def test_generate_hansard_id_zero_padded(self) -> None:
        """Speech numbers below 10 should be zero-padded to two digits."""
        result = generate_hansard_id("2023-05-12", 1)
        assert result == "NZ-HANS-2023-05-12-SP-01"

    def test_generate_hansard_id_double_digit(self) -> None:
        """Speech numbers >= 10 should not be truncated."""
        result = generate_hansard_id("2023-05-12", 42)
        assert result == "NZ-HANS-2023-05-12-SP-42"

    def test_generate_hansard_id_matches_pattern(self) -> None:
        """Verify the general pattern."""
        result = generate_hansard_id("2023-05-12", 7)
        assert re.fullmatch(r"NZ-HANS-\d{4}-\d{2}-\d{2}-SP-\d{2}", result)


# ---------------------------------------------------------------------------
# Sentence Chunking
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def nlp() -> Language:
    """Return a spaCy pipeline with sentence segmentation enabled."""
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner", "lemmatizer"])
    if "parser" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")
    return nlp


class TestChunkBySentence:
    """Tests for :func:`chunk_by_sentence`."""

    def test_chunk_by_sentence_returns_list(self, nlp: Language) -> None:
        """Return type should be a list."""
        result = chunk_by_sentence("Hello world.", nlp)
        assert isinstance(result, list)

    def test_chunk_by_sentence_multiple_sentences(self, nlp: Language) -> None:
        """Multiple sentences should produce multiple chunks."""
        text = "First sentence. Second sentence. Third sentence."
        result = chunk_by_sentence(text, nlp)
        assert len(result) == 3  # noqa: PLR2004

    def test_chunk_by_sentence_single_sentence(self, nlp: Language) -> None:
        """A single sentence should produce exactly one chunk."""
        result = chunk_by_sentence("This is one sentence.", nlp)
        assert len(result) == 1

    def test_chunk_by_sentence_empty_text(self, nlp: Language) -> None:
        """Empty text should return an empty list."""
        result = chunk_by_sentence("", nlp)
        assert result == []

    def test_chunk_by_sentence_has_required_keys(self, nlp: Language) -> None:
        """Each chunk dict must contain the required keys."""
        result = chunk_by_sentence("Test sentence.", nlp)
        chunk = result[0]
        assert "doc_id" in chunk
        assert "text" in chunk
        assert "sentence_num" in chunk
        assert "char_start" in chunk
        assert "char_end" in chunk

    def test_chunk_by_sentence_char_offsets(self, nlp: Language) -> None:
        """Character offsets should align with the original text."""
        text = "First. Second."
        result = chunk_by_sentence(text, nlp)
        assert len(result) == 2  # noqa: PLR2004

        reconstructed = text[result[0]["char_start"] : result[0]["char_end"]]
        assert reconstructed == result[0]["text"]

        reconstructed2 = text[result[1]["char_start"] : result[1]["char_end"]]
        assert reconstructed2 == result[1]["text"]

    def test_chunk_by_sentence_sentence_num_sequential(self, nlp: Language) -> None:
        """sentence_num should be zero-based and sequential."""
        text = "Go. Stop. Wait. Run."
        result = chunk_by_sentence(text, nlp)
        nums = [c["sentence_num"] for c in result]
        assert nums == [0, 1, 2, 3]

    def test_chunk_by_sentence_doc_id_placeholder(self, nlp: Language) -> None:
        """Default doc_id should be '?'."""
        result = chunk_by_sentence("Test.", nlp)
        assert result[0]["doc_id"] == "?"

    def test_chunk_by_sentence_text_preserved(self, nlp: Language) -> None:
        """Sentence text should be preserved exactly."""
        text = "This is a test sentence with macrons: ā, ē, ī, ō, ū."
        result = chunk_by_sentence(text, nlp)
        assert result[0]["text"] == text


class TestChunkLegislationDocument:
    """Tests for :func:`chunk_legislation_document`."""

    def test_chunk_legislation_document_returns_list(self, nlp: Language) -> None:
        """Return type should be a list."""
        text = "Section 1. Section 2."
        result = chunk_legislation_document(text, nlp, 2023, 42)
        assert isinstance(result, list)

    def test_chunk_legislation_document_ids(self, nlp: Language) -> None:
        """Each chunk should have a sequential legislation ID."""
        text = "First. Second. Third."
        result = chunk_legislation_document(text, nlp, 2024, 7)
        assert len(result) == 3  # noqa: PLR2004
        assert result[0]["doc_id"] == "NZ-ACT-2024-007-SEC-0"
        assert result[1]["doc_id"] == "NZ-ACT-2024-007-SEC-1"
        assert result[2]["doc_id"] == "NZ-ACT-2024-007-SEC-2"


class TestChunkHansardSpeech:
    """Tests for :func:`chunk_hansard_speech`."""

    def test_chunk_hansard_speech_returns_list(self, nlp: Language) -> None:
        """Return type should be a list."""
        text = "Kia ora. Tēnā koutou."
        result = chunk_hansard_speech(text, nlp, "2023-05-12", 3)
        assert isinstance(result, list)

    def test_chunk_hansard_speech_ids(self, nlp: Language) -> None:
        """Each chunk should have the same Hansard ID."""
        text = "First. Second."
        result = chunk_hansard_speech(text, nlp, "2023-05-12", 3)
        assert len(result) == 2  # noqa: PLR2004
        assert result[0]["doc_id"] == "NZ-HANS-2023-05-12-SP-03"
        assert result[1]["doc_id"] == "NZ-HANS-2023-05-12-SP-03"
