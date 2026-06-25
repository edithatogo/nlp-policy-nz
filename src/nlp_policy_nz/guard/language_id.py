"""Phrase-level language identifier for Te Reo Māori vs English detection.

Provides structured detection results using the ``lingua`` library,
supporting full-text language identification, batch sentence detection,
and code-switching segmentation for bilingual texts in the
``nlp-policy-nz`` pipeline.
"""

from __future__ import annotations

import typing as ty

import msgspec
from lingua import Language, LanguageDetector, LanguageDetectorBuilder

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LANGUAGE_MIIO_CONFIDENCE: ty.Final[float] = 0.7
"""Minimum confidence threshold for a detection to be considered reliable."""

# ---------------------------------------------------------------------------
# Structured result type
# ---------------------------------------------------------------------------


class LanguageResult(msgspec.Struct, frozen=True):
    r"""Result of a single language-detection query.

    Attributes
    ----------
    language : str
        ISO 639-1 code of the detected language (``\"en\"`` or ``\"mi\"``).
    confidence : float
        Detection confidence score in ``[0.0, 1.0]``.
    is_reliable : bool
        ``True`` when *confidence* meets or exceeds
        :data:`LANGUAGE_MIIO_CONFIDENCE`.

    """

    language: str
    confidence: float
    is_reliable: bool


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class LanguageIdentifier:
    """Detect Te Reo Māori and English at the phrase level.

    Wraps a ``lingua`` :class:`LanguageDetector` pre-configured to
    distinguish between English and Māori.  The detector models are
    loaded once at construction time.

    Parameters
    ----------
    min_confidence : float
        Confidence threshold used to populate
        :attr:`LanguageResult.is_reliable`.  Defaults to
        :data:`LANGUAGE_MIIO_CONFIDENCE`.

    """

    def __init__(self, min_confidence: float = LANGUAGE_MIIO_CONFIDENCE) -> None:
        """Initialize the instance."""
        self._min_confidence = min_confidence
        self._detector: LanguageDetector = (
            LanguageDetectorBuilder.from_languages(Language.ENGLISH, Language.MAORI)
            .with_low_accuracy_mode()
            .build()
        )

    # -- Public API ---------------------------------------------------------

    def detect(self, text: str) -> LanguageResult:
        """Detect the language of *text*.

        Parameters
        ----------
        text : str
            Input text to classify.

        Returns
        -------
        LanguageResult
            Detection result with ISO code, confidence score, and
            reliability flag.

        """
        if not text or not text.strip():
            return LanguageResult(language="en", confidence=0.0, is_reliable=False)

        detected: Language | None = self._detector.detect_language_of(text)
        iso_code = self._to_iso(detected)
        if detected is not None:
            confidence = self._detector.compute_language_confidence(text, detected)
        else:
            confidence = 0.0

        return LanguageResult(
            language=iso_code,
            confidence=confidence,
            is_reliable=confidence >= self._min_confidence,
        )

    def detect_sentences(self, sentences: list[str]) -> list[LanguageResult]:
        """Batch-detect language for a list of sentences.

        Parameters
        ----------
        sentences : list[str]
            One or more text strings to classify independently.

        Returns
        -------
        list[LanguageResult]
            A detection result for each input sentence, preserving order.

        """
        return [self.detect(s) for s in sentences]

    def detect_code_switching(self, text: str) -> list[tuple[str, str]]:
        """Split *text* into contiguous single-language segments.

        Uses lingua's built-in multilingual detection to identify
        boundaries where the language switches between English and
        Māori.

        Parameters
        ----------
        text : str
            Mixed-language input text.

        Returns
        -------
        list[tuple[str, str]]
            A list of ``(language_iso_code, segment)`` tuples, where
            each segment is a maximal contiguous substring identified
            as being in that language.  The concatenation of all
            segments reconstructs the original *text*.

        """
        if not text or not text.strip():
            return []

        results = self._detector.detect_multiple_languages_of(text)
        segments: list[tuple[str, str]] = []

        for result in results:
            iso = self._to_iso(result.language)
            segment = text[result.start_index : result.end_index]
            segments.append((iso, segment))

        return segments

    # -- Internal helpers ---------------------------------------------------

    @staticmethod
    def _to_iso(language: Language | None) -> str:
        r"""Map a lingua ``Language`` enum to its ISO 639-1 code.

        Parameters
        ----------
        language : Language | None
            The lingua language enum value, or ``None`` if detection
            was inconclusive.

        Returns
        -------
        str
            ``\"en\"`` for English, ``\"mi\"`` for Māori, or ``\"un\"``
            (unknown) when *language* is ``None`` or unrecognised.

        """
        if language is None:
            return "un"
        if language == Language.ENGLISH:
            return "en"
        if language == Language.MAORI:
            return "mi"
        # Fallback: use the iso_code_639_1 attribute if available.
        code: str | None = language.iso_code_639_1
        return code if code is not None else "un"
