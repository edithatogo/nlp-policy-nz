"""Document chunking and structural ID generation for NZ legislation and Hansard.

This module provides functions for splitting documents into sentence-level
chunks and assigning unique structural identifiers following NZ conventions:

- Legislation: ``NZ-ACT-{YEAR}-{NUMBER}-SEC-{SECTION}``
- Hansard:     ``NZ-HANS-{YYYY-MM-DD}-SP-{SPEECH_NUM}``
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spacy.language import Language

# ---------------------------------------------------------------------------
# ID Patterns
# ---------------------------------------------------------------------------

CHUNK_ID_PATTERN: str = (
    "Legislation: NZ-ACT-{YEAR}-{NUMBER}-SEC-{SECTION} | "
    "Hansard: NZ-HANS-{YYYY-MM-DD}-SP-{SPEECH_NUM}"
)
"""Description of the two chunk-ID formats used in this project."""

# ---------------------------------------------------------------------------
# ID Generation
# ---------------------------------------------------------------------------


def generate_legislation_id(year: int, number: int, section: str | int) -> str:
    r"""Generate a structured document ID for a legislation chunk.

    The returned ID follows the pattern
    ``NZ-ACT-{YEAR}-{NNN}-SEC-{SECTION}``, where *NNN* is the act number
    zero-padded to three digits.

    Args:
        year: Enactment year (e.g. ``1961``).
        number: Act number (e.g. ``43``).
        section: Section identifier (e.g. ``4`` or ``\"4\"``).

    Returns:
        Fully qualified chunk ID string.

    Example:
        >>> generate_legislation_id(1961, 43, 4)
        'NZ-ACT-1961-043-SEC-4'

    """
    return f"NZ-ACT-{year}-{number:03d}-SEC-{section}"


def generate_hansard_id(date: str, speech_num: int) -> str:
    r"""Generate a structured document ID for a Hansard speech chunk.

    The returned ID follows the pattern
    ``NZ-HANS-{YYYY-MM-DD}-SP-{NN}``, where *NN* is the speech number
    zero-padded to two digits.

    Args:
        date: Speech date in ``YYYY-MM-DD`` format (e.g. ``\"2023-05-12\"``).
        speech_num: Speech number (e.g. ``4``).

    Returns:
        Fully qualified chunk ID string.

    Example:
        >>> generate_hansard_id(\"2023-05-12\", 4)
        'NZ-HANS-2023-05-12-SP-04'

    """
    return f"NZ-HANS-{date}-SP-{speech_num:02d}"


# ---------------------------------------------------------------------------
# Sentence Chunking
# ---------------------------------------------------------------------------


def chunk_by_sentence(text: str, nlp: Language) -> list[dict[str, Any]]:
    r"""Split *text* into sentence chunks using a spaCy ``Language`` pipeline.

    Each chunk is represented as a dictionary with the following keys:

    - **doc_id**:       Placeholder string (``\"?\"``) — the caller should
                        overwrite this with a meaningful identifier.
    - **text**:         The raw sentence text.
    - **sentence_num**: Zero-based sentence index within the document.
    - **char_start**:   Character offset of the first character of the
                        sentence in the original *text*.
    - **char_end**:     Character offset of the first character *after* the
                        sentence in the original *text*.

    Args:
        text: Raw document text to segment into sentences.
        nlp:  Loaded spaCy ``Language`` object with sentence segmentation
              enabled (e.g. ``sentencizer`` or a full parser pipeline).

    Returns:
        A list of sentence-chunk dictionaries.

    Example:
        >>> import spacy
        >>> nlp = spacy.load(\"en_core_web_sm\", disable=[\"tagger\", \"ner\"])
        >>> chunks = chunk_by_sentence(\"First. Second.\", nlp)
        >>> len(chunks)
        2
        >>> chunks[0][\"text\"]
        'First.'

    """
    doc = nlp(text)
    chunks: list[dict[str, Any]] = []

    for i, sent in enumerate(doc.sents):
        chunks.append(
            {
                "doc_id": "?",
                "text": sent.text,
                "sentence_num": i,
                "char_start": sent.start_char,
                "char_end": sent.end_char,
            }
        )

    return chunks


def chunk_legislation_document(
    text: str,
    nlp: Language,
    year: int,
    number: int,
) -> list[dict[str, Any]]:
    """Chunk a piece of legislation into sentence-level chunks with IDs.

    Each chunk is assigned a sequential section identifier so that the
    resulting ``doc_id`` values follow the pattern
    ``NZ-ACT-{YEAR}-{NNN}-SEC-{N}`` (e.g. ``NZ-ACT-1961-043-SEC-0``,
    ``...-SEC-1``, etc.).

    Args:
        text:   Full text of the legislation document.
        nlp:    Loaded spaCy ``Language`` object.
        year:   Enactment year.
        number: Act number.

    Returns:
        List of sentence-chunk dictionaries with populated ``doc_id`` fields.

    """
    chunks = chunk_by_sentence(text, nlp)

    for i, chunk in enumerate(chunks):
        chunk["doc_id"] = generate_legislation_id(year, number, i)

    return chunks


def chunk_hansard_speech(
    text: str,
    nlp: Language,
    date: str,
    speech_num: int,
) -> list[dict[str, Any]]:
    """Chunk a Hansard speech into sentence-level chunks with IDs.

    Each chunk is assigned a ``doc_id`` following the pattern
    ``NZ-HANS-{YYYY-MM-DD}-SP-{NN}``, where the speech number is
    zero-padded to two digits.

    Args:
        text:       Full text of the Hansard speech.
        nlp:        Loaded spaCy ``Language`` object.
        date:       Speech date in ``YYYY-MM-DD`` format.
        speech_num: Speech number.

    Returns:
        List of sentence-chunk dictionaries with populated ``doc_id`` fields.

    """
    chunks = chunk_by_sentence(text, nlp)

    for _i, chunk in enumerate(chunks):
        chunk["doc_id"] = generate_hansard_id(date, speech_num)

    return chunks
