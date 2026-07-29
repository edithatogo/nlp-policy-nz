"""Typed documents and extractive answers for Haystack governance orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GovernanceDocument:
    """A governance-scoped document flowing through the orchestration DAG."""

    id: str
    content: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExtractedSpanAnswer:
    """An extractive answer anchored to source offsets."""

    answer: str
    document_id: str
    start: int
    end: int
    score: float
    model_id: str
    pipeline_version: str

    def is_verbatim_of(self, source: str) -> bool:
        """Return True when the answer matches the source slice at ``start:end``."""
        if self.start < 0 or self.end > len(source):
            return False
        return source[self.start : self.end] == self.answer
