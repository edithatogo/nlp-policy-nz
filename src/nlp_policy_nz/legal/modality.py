"""Deontic modality detection for New Zealand legal text."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from spacy.language import Language
from spacy.tokens import Doc, Span, Token

__all__ = [
    "DEONTIC_PATTERNS",
    "DeonticModality",
    "DeonticModalityDetector",
    "ModalityAnnotation",
    "detect_modality",
]


class DeonticModality(Enum):
    """Deontic modality classes used for legal effect analysis."""

    OBLIGATION = "obligation"
    PROHIBITION = "prohibition"
    PERMISSION = "permission"
    DISPENSATION = "dispensation"


@dataclass(frozen=True)
class ModalityAnnotation:
    """A detected deontic trigger and its governed scope."""

    modality: DeonticModality
    trigger: str
    scope: str | None
    start: int
    end: int

    def to_dict(self) -> dict[str, str | int | None]:
        """Return a serialization-friendly annotation dictionary."""
        data = asdict(self)
        data["modality"] = self.modality.value
        return data


DEONTIC_PATTERNS: dict[str, dict[str, Any]] = {
    "must_not": {
        "modality": DeonticModality.PROHIBITION,
        "tokens": ("must", "not"),
    },
    "shall_not": {
        "modality": DeonticModality.PROHIBITION,
        "tokens": ("shall", "not"),
    },
    "need_not": {
        "modality": DeonticModality.DISPENSATION,
        "tokens": ("need", "not"),
    },
    "must": {
        "modality": DeonticModality.OBLIGATION,
        "tokens": ("must",),
    },
    "shall": {
        "modality": DeonticModality.OBLIGATION,
        "tokens": ("shall",),
    },
    "may": {
        "modality": DeonticModality.PERMISSION,
        "tokens": ("may",),
    },
}
"""NZ legislative deontic trigger patterns ordered from specific to general."""


def _ensure_extensions() -> None:
    """Register spaCy extensions used by the modality detector."""
    if not Token.has_extension("modality"):
        Token.set_extension("modality", default=None)
    if not Token.has_extension("modality_scope"):
        Token.set_extension("modality_scope", default=None)
    if not Token.has_extension("modality_annotation"):
        Token.set_extension("modality_annotation", default=None)
    if not Doc.has_extension("modality_annotations"):
        Doc.set_extension("modality_annotations", default=None)


_ensure_extensions()


@Language.factory("deontic_modality", default_config={"patterns": None})
class DeonticModalityDetector:
    """spaCy component that detects deontic modality in legal clauses."""

    def __init__(
        self,
        nlp: Language,
        name: str = "deontic_modality",
        patterns: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Initialize the instance."""
        self.name = name
        self.vocab = nlp.vocab
        self.patterns = patterns if patterns is not None else DEONTIC_PATTERNS
        self._ordered_patterns = sorted(
            self.patterns.values(),
            key=lambda pattern: len(pattern["tokens"]),
            reverse=True,
        )

    def __call__(self, doc: Doc) -> Doc:
        """Annotate deontic modality triggers on a spaCy document."""
        annotations: list[ModalityAnnotation] = []
        consumed: set[int] = set()

        for i, token in enumerate(doc):
            if i in consumed:
                continue

            match = self._match_at(doc, i)
            if match is None:
                continue

            trigger_tokens, modality = match
            trigger_span = doc[i : i + len(trigger_tokens)]
            scope = self._resolve_scope(trigger_span)
            annotation = ModalityAnnotation(
                modality=modality,
                trigger=trigger_span.text,
                scope=scope,
                start=trigger_span.start_char,
                end=trigger_span.end_char,
            )

            token._.modality = modality.value
            token._.modality_scope = scope
            token._.modality_annotation = annotation
            annotations.append(annotation)
            consumed.update(range(i, i + len(trigger_tokens)))

        doc._.modality_annotations = annotations
        return doc

    def _match_at(self, doc: Doc, start: int) -> tuple[tuple[str, ...], DeonticModality] | None:
        """Return the longest deontic pattern matching at token index *start*."""
        for pattern in self._ordered_patterns:
            tokens: tuple[str, ...] = tuple(pattern["tokens"])
            end = start + len(tokens)
            if end > len(doc):
                continue
            if tuple(token.lower_ for token in doc[start:end]) == tokens:
                modality = pattern["modality"]
                if isinstance(modality, str):
                    modality = DeonticModality(modality)
                return tokens, modality
        return None

    def _resolve_scope(self, trigger: Span) -> str | None:
        """Resolve the governed clause for a deontic trigger."""
        head = trigger[0].head
        if head.i not in range(trigger.start, trigger.end) and head.pos_ in {"VERB", "AUX"}:
            subtree = [
                token
                for token in head.subtree
                if token.i not in range(trigger.start, trigger.end) and not token.is_punct
            ]
            if subtree:
                return " ".join(token.text for token in sorted(subtree, key=lambda item: item.i))

        return self._fallback_scope(trigger)

    @staticmethod
    def _fallback_scope(trigger: Span) -> str | None:
        """Return text after the trigger up to punctuation when no parse is available."""
        scope_tokens: list[str] = []
        for token in trigger.doc[trigger.end :]:
            if token.is_punct or token.text in {";", "."}:
                break
            scope_tokens.append(token.text)
        if not scope_tokens:
            return None
        return " ".join(scope_tokens)

    def to_disk(self, _path: str, **_kwargs: object) -> None:
        """Serialize the component.

        Patterns are code-defined, so there is no on-disk state.
        """

    def from_disk(self, _path: str, **_kwargs: object) -> DeonticModalityDetector:
        """Deserialize the component and return ``self``."""
        return self


def detect_modality(text: str, nlp: Language) -> list[ModalityAnnotation]:
    """Detect deontic modality annotations in *text* using *nlp*."""
    if "deontic_modality" not in nlp.pipe_names:
        nlp.add_pipe("deontic_modality", last=True)
    doc = nlp(text)
    annotations = doc._.modality_annotations
    return list(annotations or [])
