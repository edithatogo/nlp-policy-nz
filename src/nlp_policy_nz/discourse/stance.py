"""Policy stance classification for debate text."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Stance = Literal["pro", "con", "neutral"]

PRO_CUES: tuple[str, ...] = (
    "support",
    "commend",
    "should pass",
    "must pass",
    "will help",
    "improve",
)
CON_CUES: tuple[str, ...] = (
    "oppose",
    "reject",
    "should be rejected",
    "harmful",
    "raises costs",
    "against",
)


@dataclass(frozen=True)
class StanceResult:
    """One stance classification result."""

    stance: Stance
    confidence: float
    evidence: str | None = None

    def to_dict(self) -> dict[str, str | float | None]:
        """Return a schema-safe stance result dictionary."""
        return {
            "stance": self.stance,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


class StanceClassifier:
    """Cue-backed stance classifier for parliamentary policy text."""

    def classify(self, text: str, *, issue: str | None = None) -> StanceResult:
        """Classify text as pro, con, or neutral for a policy issue."""
        folded = text.casefold()
        pro_score = sum(cue in folded for cue in PRO_CUES)
        con_score = sum(cue in folded for cue in CON_CUES)
        if pro_score > con_score:
            return StanceResult("pro", 0.9, issue)
        if con_score > pro_score:
            return StanceResult("con", 0.9, issue)
        return StanceResult("neutral", 0.75, issue)


def evaluate_stance_accuracy(
    labelled_segments: list[dict[str, str]],
    *,
    classifier: StanceClassifier | None = None,
) -> float:
    """Evaluate stance accuracy on labelled debate segments."""
    active_classifier = classifier or StanceClassifier()
    if not labelled_segments:
        return 0.0
    correct = sum(
        active_classifier.classify(case["text"]).stance == case["stance"]
        for case in labelled_segments
    )
    return correct / len(labelled_segments)
