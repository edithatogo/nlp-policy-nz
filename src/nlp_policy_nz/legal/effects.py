"""Rule-based legal effect classification for New Zealand legal text."""

from __future__ import annotations

from enum import Enum

from nlp_policy_nz.legal.modality import DeonticModality, detect_modality


class LegalEffect(Enum):
    """LKIF-inspired legal effect categories."""

    OBLIGATION = "obligation"
    PROHIBITION = "prohibition"
    PERMISSION = "permission"
    POWER = "power"
    LIABILITY = "liability"
    IMMUNITY = "immunity"
    DISABILITY = "disability"

    def __str__(self) -> str:
        """Return the serialized legal effect value."""
        return self.value


_POWER_MARKERS = (
    "may make regulations",
    "may appoint",
    "may delegate",
    "has power",
    "has the power",
    "is empowered",
)
_LIABILITY_MARKERS = (
    "is liable",
    "liable on conviction",
    "commits an offence",
    "penalty",
)
_IMMUNITY_MARKERS = (
    "is not liable",
    "no liability",
    "immune from",
    "immunity",
)
_DISABILITY_MARKERS = (
    "must not exercise",
    "shall not exercise",
    "is disqualified",
    "not eligible",
)

_MODALITY_PRIORITY: dict[DeonticModality, LegalEffect] = {
    DeonticModality.PROHIBITION: LegalEffect.PROHIBITION,
    DeonticModality.OBLIGATION: LegalEffect.OBLIGATION,
    DeonticModality.PERMISSION: LegalEffect.PERMISSION,
    DeonticModality.DISPENSATION: LegalEffect.PERMISSION,
}


def classify_legal_effect(text: str, nlp: object | None = None) -> str | None:
    """Classify a clause or section into a legal effect category."""
    normalised = " ".join(text.casefold().split())
    effect: str | None = None
    if not normalised:
        effect = None
    elif any(marker in normalised for marker in _IMMUNITY_MARKERS):
        effect = LegalEffect.IMMUNITY.value
    elif any(marker in normalised for marker in _LIABILITY_MARKERS):
        effect = LegalEffect.LIABILITY.value
    elif any(marker in normalised for marker in _DISABILITY_MARKERS):
        effect = LegalEffect.DISABILITY.value
    elif any(marker in normalised for marker in _POWER_MARKERS):
        effect = LegalEffect.POWER.value
    elif nlp is not None:
        annotations = detect_modality(text, nlp)  # type: ignore[arg-type]
        if annotations:
            for modality, legal_effect in _MODALITY_PRIORITY.items():
                if any(annotation.modality == modality for annotation in annotations):
                    effect = legal_effect.value
                    break

    if effect is None:
        if "must not" in normalised or "shall not" in normalised:
            effect = LegalEffect.PROHIBITION.value
        elif "must" in normalised or "shall" in normalised:
            effect = LegalEffect.OBLIGATION.value
        elif "may" in normalised or "need not" in normalised:
            effect = LegalEffect.PERMISSION.value

    return effect
