"""Silver-label consensus helpers for Track 13 argument annotation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Any, Literal

LabelField = Literal["claim_label", "premise_label", "relation_label"]

LABEL_FIELDS: tuple[LabelField, ...] = ("claim_label", "premise_label", "relation_label")
DEFAULT_AI_PROVIDERS: tuple[str, ...] = (
    "cline",
    "opencode",
    "mimo",
    "agy",
    "agent",
    "openrouter",
    "nvidia_nim",
)
DEFAULT_PROVIDER_COMMANDS: dict[str, tuple[str, ...]] = {
    "cline": ("cline",),
    "opencode": ("opencode",),
    "mimo": ("mimo",),
    "agy": ("agy",),
    "agent": ("agent",),
    "openrouter": ("openrouter",),
    "nvidia_nim": ("nvidia-nim", "nim"),
}
TRACK13_LABEL_SCHEMA: dict[str, list[str]] = {
    "claim_label": ["claim", "major_claim", "non_argument"],
    "premise_label": ["premise", "evidence", "none"],
    "relation_label": ["support", "attack", "none"],
}
BIOMEDICAL_ONTOLOGY_PROVIDER = "ontology_bridge"
HUMAN_SOURCE_WEIGHT = 1.0
AI_PROVIDER_WEIGHT = 0.5
WEAK_RULE_WEIGHT = 0.25
MIN_CONSENSUS_SCORE = 0.67
MIN_INDEPENDENT_AI_VOTES = 3


@dataclass(frozen=True)
class ProviderAvailability:
    """Availability status for one external labelling provider."""

    provider: str
    available: bool
    executable: str | None = None


@dataclass(frozen=True)
class SilverVote:
    """One provider/source vote for a Track 13 label."""

    record_id: str
    provider: str
    source_type: Literal["human_calibration", "ai_provider", "weak_rule"]
    claim_label: str
    premise_label: str
    relation_label: str
    confidence: float = 1.0

    @property
    def weight(self) -> float:
        """Return the configured vote weight for this source type."""
        base_weight = {
            "human_calibration": HUMAN_SOURCE_WEIGHT,
            "ai_provider": AI_PROVIDER_WEIGHT,
            "weak_rule": WEAK_RULE_WEIGHT,
        }[self.source_type]
        return base_weight * max(0.0, min(self.confidence, 1.0))


@dataclass(frozen=True)
class OntologyConcept:
    """One HPO/UMLS/SNOMED-aligned concept used as weak context evidence."""

    concept_id: str
    label: str
    ontology: str
    hpo_id: str | None = None
    xrefs: tuple[str, ...] = ()


@dataclass(frozen=True)
class SilverConsensus:
    """Aggregated silver-label decision for one Track 13 record."""

    record_id: str
    claim_label: str
    premise_label: str
    relation_label: str
    consensus_score: float
    sources: tuple[str, ...]
    accepted: bool
    disagreement: bool

    def to_json_record(self, text: str) -> dict[str, Any]:
        """Return a JSONL-ready silver-label record."""
        return {
            "record_id": self.record_id,
            "text": text,
            "claim_label": self.claim_label,
            "premise_label": self.premise_label,
            "relation_label": self.relation_label,
            "silver_label": self.accepted,
            "consensus_score": round(self.consensus_score, 6),
            "sources": list(self.sources),
        }


def make_target_record(record_id: str, text: str) -> dict[str, str]:
    """Return a Track 13 target-corpus record from raw NZ policy text."""
    stripped = " ".join(text.split())
    if not stripped:
        raise ValueError("Track 13 target record text must not be empty")
    return {"record_id": record_id, "text": stripped}


def build_provider_prompt(record_id: str, text: str) -> str:
    """Build a provider-neutral prompt for external AI labelling agents."""
    schema = "\n".join(
        f"- {field}: {', '.join(values)}" for field, values in TRACK13_LABEL_SCHEMA.items()
    )
    return (
        "Label this New Zealand policy/legal text for Track 13 argument structure.\n"
        "Return exactly one JSON object with keys: record_id, provider, source_type, "
        "claim_label, premise_label, relation_label, confidence.\n"
        "Use source_type='ai_provider'. Do not add explanations.\n\n"
        f"Allowed labels:\n{schema}\n\n"
        f"record_id: {record_id}\n"
        f"text: {text}"
    )


def match_ontology_concepts(text: str, concepts: list[OntologyConcept]) -> list[OntologyConcept]:
    """Return ontology concepts with labels that appear in text."""
    folded = f" {text.casefold()} "
    matches: list[OntologyConcept] = []
    for concept in concepts:
        label = concept.label.casefold().strip()
        if label and f" {label} " in folded:
            matches.append(concept)
    return matches


def ontology_bridge_vote(
    record_id: str,
    text: str,
    concepts: list[OntologyConcept],
) -> SilverVote | None:
    """Create a weak-rule vote when HPO/UMLS/SNOMED-aligned terms appear."""
    matches = match_ontology_concepts(text, concepts)
    if not matches:
        return None
    confidence = min(1.0, 0.5 + (0.1 * len({match.concept_id for match in matches})))
    return SilverVote(
        record_id=record_id,
        provider=BIOMEDICAL_ONTOLOGY_PROVIDER,
        source_type="weak_rule",
        claim_label="non_argument",
        premise_label="none",
        relation_label="none",
        confidence=confidence,
    )


def discover_provider_availability(
    commands: dict[str, tuple[str, ...]] | None = None,
) -> list[ProviderAvailability]:
    """Return local executable availability for configured providers."""
    command_map = commands or DEFAULT_PROVIDER_COMMANDS
    availability: list[ProviderAvailability] = []
    for provider, candidates in command_map.items():
        executable = next((found for command in candidates if (found := which(command))), None)
        availability.append(
            ProviderAvailability(
                provider=provider,
                available=executable is not None,
                executable=executable,
            )
        )
    return availability


def aggregate_silver_votes(
    record_id: str,
    votes: list[SilverVote],
    *,
    minimum_independent_ai_votes: int = MIN_INDEPENDENT_AI_VOTES,
    minimum_consensus_score: float = MIN_CONSENSUS_SCORE,
) -> SilverConsensus:
    """Aggregate provider votes into one auditable silver-label decision."""
    scoped_votes = [vote for vote in votes if vote.record_id == record_id]
    if not scoped_votes:
        raise ValueError(f"no votes supplied for record_id={record_id!r}")

    labels = {field: _weighted_winner(scoped_votes, field) for field in LABEL_FIELDS}
    total_weight = sum(vote.weight for vote in scoped_votes)
    winning_weight = sum(score for _, score in labels.values())
    consensus_score = winning_weight / (total_weight * len(LABEL_FIELDS))
    ai_voters = {vote.provider for vote in scoped_votes if vote.source_type == "ai_provider"}
    has_human_calibration = any(vote.source_type == "human_calibration" for vote in scoped_votes)
    enough_independence = len(ai_voters) >= minimum_independent_ai_votes or (
        has_human_calibration and len(ai_voters) >= 2
    )
    accepted = enough_independence and consensus_score >= minimum_consensus_score
    sources = tuple(sorted({vote.provider for vote in scoped_votes}))
    return SilverConsensus(
        record_id=record_id,
        claim_label=labels["claim_label"][0],
        premise_label=labels["premise_label"][0],
        relation_label=labels["relation_label"][0],
        consensus_score=consensus_score,
        sources=sources,
        accepted=accepted,
        disagreement=not accepted,
    )


def load_votes_jsonl(path: str | Path) -> list[SilverVote]:
    """Load Track 13 provider votes from JSONL."""
    import json

    votes: list[SilverVote] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        try:
            votes.append(SilverVote(**payload))
        except TypeError as exc:
            raise ValueError(f"invalid Track 13 vote JSONL at line {line_number}") from exc
    return votes


def _weighted_winner(votes: list[SilverVote], field: LabelField) -> tuple[str, float]:
    """Return the highest-weight label for one field."""
    scores: defaultdict[str, float] = defaultdict(float)
    for vote in votes:
        scores[str(getattr(vote, field))] += vote.weight
    return max(scores.items(), key=lambda item: (item[1], item[0]))
