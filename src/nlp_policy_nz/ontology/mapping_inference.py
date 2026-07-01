"""Reviewable ontology mapping inference helpers for Track 30."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal

from nlp_policy_nz.ontology.mapping_graph import MappingPredicate, OntologyMappingRecord

if TYPE_CHECKING:
    from collections.abc import Callable

InferenceMethod = Literal["exact", "fuzzy", "synonym", "structural", "embedding", "llm_prompt"]

INFERRED_MAPPING_MANIFEST_FILENAME: Final[str] = "inferred_mapping_candidates.json"
LLM_INTERPRETATION_PROMPT_FILENAME: Final[str] = "mapping_interpretation_prompt.json"
_WORD_RE: Final[re.Pattern[str]] = re.compile(r"[a-z0-9]+")
_STRONGEST_PREDICATES: Final[tuple[MappingPredicate, ...]] = (
    "owl:equivalentClass",
    "owl:equivalentProperty",
    "skos:exactMatch",
    "skos:closeMatch",
    "skos:relatedMatch",
    "skos:broadMatch",
    "skos:narrowMatch",
    "source:crosswalk",
)
_METHOD_ORDER: Final[tuple[InferenceMethod, ...]] = (
    "exact",
    "synonym",
    "fuzzy",
    "structural",
    "embedding",
    "llm_prompt",
)


@dataclass(frozen=True, slots=True)
class OntologyTerm:
    """A compact ontology term used by deterministic mapping inference."""

    standard: str
    term_id: str
    label: str
    definition: str = ""
    synonyms: tuple[str, ...] = ()
    parents: tuple[str, ...] = ()
    children: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate required identity fields."""
        for field_name in ("standard", "term_id", "label"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")

    @property
    def key(self) -> str:
        """Return a stable standard-local key."""
        return f"{self.standard.strip()}::{self.term_id.strip()}"

    @property
    def normalized_label(self) -> str:
        """Return a normalized label for lexical matching."""
        return normalize_mapping_text(self.label)

    @property
    def normalized_aliases(self) -> tuple[str, ...]:
        """Return normalized labels, IDs, definitions, and synonyms."""
        values = (self.term_id, self.label, self.definition, *self.synonyms)
        return tuple(
            dict.fromkeys(normalize_mapping_text(value) for value in values if value.strip())
        )


@dataclass(frozen=True, slots=True)
class InferredMappingCandidate:
    """A non-authoritative mapping candidate that must be reviewed before use."""

    source: OntologyTerm
    target: OntologyTerm
    mapping_predicate: MappingPredicate
    methods: tuple[InferenceMethod, ...]
    confidence: float
    evidence: tuple[str, ...]
    review_status: Literal["needs_review"] = "needs_review"
    inferred: bool = True

    def __post_init__(self) -> None:
        """Validate candidate review boundary fields."""
        if not self.methods:
            raise ValueError("at least one inference method is required")
        if not self.evidence:
            raise ValueError("at least one evidence item is required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.review_status != "needs_review":
            raise ValueError("inferred candidates must require review")
        if not self.inferred:
            raise ValueError("candidate must be marked inferred")

    @property
    def candidate_id(self) -> str:
        """Return a deterministic candidate identifier."""
        source = slugify_mapping_token(f"{self.source.standard}-{self.source.term_id}")
        target = slugify_mapping_token(f"{self.target.standard}-{self.target.term_id}")
        return f"inferred-{source}-to-{target}"

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready candidate data."""
        return {
            "candidate_id": self.candidate_id,
            "source_standard": self.source.standard,
            "target_standard": self.target.standard,
            "source_term": self.source.term_id,
            "target_term": self.target.term_id,
            "source_label": self.source.label,
            "target_label": self.target.label,
            "mapping_predicate": self.mapping_predicate,
            "methods": list(self.methods),
            "confidence": round(self.confidence, 4),
            "evidence": list(self.evidence),
            "review_status": self.review_status,
            "inferred": self.inferred,
        }

    def to_mapping_record(self, provenance: str) -> OntologyMappingRecord:
        """Convert the candidate into a Track 29 reviewable mapping record."""
        return OntologyMappingRecord(
            mapping_id=self.candidate_id,
            source_standard=self.source.standard,
            target_standard=self.target.standard,
            source_term=self.source.term_id,
            target_term=self.target.term_id,
            mapping_predicate=self.mapping_predicate,
            confidence=round(self.confidence, 4),
            method="inferred:" + ",".join(self.methods),
            provenance=provenance,
            review_status="needs_review",
            notes="; ".join((*self.evidence, "inferred=true")),
        )


def normalize_mapping_text(value: str) -> str:
    """Normalize labels and aliases for deterministic comparison."""
    return " ".join(_WORD_RE.findall(value.casefold()))


def slugify_mapping_token(value: str) -> str:
    """Return a filesystem and identifier friendly token."""
    normalized = normalize_mapping_text(value)
    return "-".join(normalized.split()) or "blank"


def infer_exact_matches(
    source_terms: tuple[OntologyTerm, ...],
    target_terms: tuple[OntologyTerm, ...],
) -> tuple[InferredMappingCandidate, ...]:
    """Infer candidates from exact normalized labels or aliases."""
    candidates: list[InferredMappingCandidate] = []
    for source in source_terms:
        source_aliases = set(source.normalized_aliases)
        for target in target_terms:
            overlap = sorted(source_aliases.intersection(target.normalized_aliases))
            if not overlap:
                continue
            candidates.append(
                InferredMappingCandidate(
                    source=source,
                    target=target,
                    mapping_predicate="skos:exactMatch",
                    methods=("exact",),
                    confidence=0.95,
                    evidence=(f"normalized alias overlap: {overlap[0]}",),
                )
            )
    return tuple(candidates)


def infer_fuzzy_matches(
    source_terms: tuple[OntologyTerm, ...],
    target_terms: tuple[OntologyTerm, ...],
    *,
    threshold: float = 0.84,
) -> tuple[InferredMappingCandidate, ...]:
    """Infer close-match candidates from normalized label and definition similarity."""
    candidates: list[InferredMappingCandidate] = []
    for source in source_terms:
        for target in target_terms:
            score, source_value, target_value = _best_similarity(source, target)
            if score < threshold:
                continue
            candidates.append(
                InferredMappingCandidate(
                    source=source,
                    target=target,
                    mapping_predicate="skos:closeMatch",
                    methods=("fuzzy",),
                    confidence=min(0.9, max(0.55, score)),
                    evidence=(
                        f"fuzzy similarity {score:.3f}: {source_value!r} ~ {target_value!r}",
                    ),
                )
            )
    return tuple(candidates)


def infer_synonym_matches(
    source_terms: tuple[OntologyTerm, ...],
    target_terms: tuple[OntologyTerm, ...],
    *,
    synonym_groups: tuple[tuple[str, ...], ...],
) -> tuple[InferredMappingCandidate, ...]:
    """Infer candidates when terms share a supplied synonym group."""
    normalized_groups = tuple(
        frozenset(normalize_mapping_text(item) for item in group if item.strip())
        for group in synonym_groups
        if group
    )
    candidates: list[InferredMappingCandidate] = []
    for source in source_terms:
        source_aliases = set(source.normalized_aliases)
        for target in target_terms:
            target_aliases = set(target.normalized_aliases)
            for group in normalized_groups:
                if source_aliases.intersection(group) and target_aliases.intersection(group):
                    candidates.append(
                        InferredMappingCandidate(
                            source=source,
                            target=target,
                            mapping_predicate="skos:closeMatch",
                            methods=("synonym",),
                            confidence=0.82,
                            evidence=(f"shared synonym group: {', '.join(sorted(group))}",),
                        )
                    )
                    break
    return tuple(candidates)


def infer_structural_matches(
    source_terms: tuple[OntologyTerm, ...],
    target_terms: tuple[OntologyTerm, ...],
    *,
    threshold: float = 0.5,
) -> tuple[InferredMappingCandidate, ...]:
    """Infer candidates from overlapping parent or child neighbourhood labels."""
    candidates: list[InferredMappingCandidate] = []
    for source in source_terms:
        source_neighbours = _normalized_neighbourhood(source)
        if not source_neighbours:
            continue
        for target in target_terms:
            target_neighbours = _normalized_neighbourhood(target)
            if not target_neighbours:
                continue
            score = _jaccard(source_neighbours, target_neighbours)
            if score < threshold:
                continue
            candidates.append(
                InferredMappingCandidate(
                    source=source,
                    target=target,
                    mapping_predicate="skos:relatedMatch",
                    methods=("structural",),
                    confidence=min(0.85, 0.55 + score / 3),
                    evidence=(f"structural neighbourhood jaccard {score:.3f}",),
                )
            )
    return tuple(candidates)


def infer_embedding_matches(
    source_terms: tuple[OntologyTerm, ...],
    target_terms: tuple[OntologyTerm, ...],
    *,
    source_vectors: dict[str, tuple[float, ...]] | None = None,
    target_vectors: dict[str, tuple[float, ...]] | None = None,
    embed_texts: Callable[[tuple[str, ...]], tuple[tuple[float, ...], ...]] | None = None,
    threshold: float = 0.8,
) -> tuple[InferredMappingCandidate, ...]:
    """Infer candidates from supplied or injected term embedding vectors."""
    resolved_source = _resolve_term_vectors(source_terms, source_vectors, embed_texts)
    resolved_target = _resolve_term_vectors(target_terms, target_vectors, embed_texts)
    candidates: list[InferredMappingCandidate] = []
    for source in source_terms:
        source_vector = resolved_source[source.key]
        for target in target_terms:
            target_vector = resolved_target[target.key]
            score = _cosine_similarity(source_vector, target_vector)
            if score < threshold:
                continue
            candidates.append(
                InferredMappingCandidate(
                    source=source,
                    target=target,
                    mapping_predicate="skos:closeMatch",
                    methods=("embedding",),
                    confidence=min(0.92, max(0.55, score)),
                    evidence=(f"embedding cosine similarity {score:.3f}",),
                )
            )
    return tuple(candidates)


def merge_inferred_candidates(
    candidates: tuple[InferredMappingCandidate, ...],
) -> tuple[InferredMappingCandidate, ...]:
    """Merge duplicate source-target candidates and boost confidence by agreement."""
    grouped: dict[tuple[str, str], list[InferredMappingCandidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[(candidate.source.key, candidate.target.key)].append(candidate)

    merged: list[InferredMappingCandidate] = []
    for group in grouped.values():
        first = group[0]
        methods = tuple(
            sorted(
                {method for candidate in group for method in candidate.methods},
                key=_METHOD_ORDER.index,
            )
        )
        evidence = tuple(dict.fromkeys(item for candidate in group for item in candidate.evidence))
        base_confidence = max(candidate.confidence for candidate in group)
        agreement_bonus = min(0.1, 0.03 * (len(methods) - 1))
        merged.append(
            InferredMappingCandidate(
                source=first.source,
                target=first.target,
                mapping_predicate=_strongest_predicate(
                    tuple(candidate.mapping_predicate for candidate in group)
                ),
                methods=methods,
                confidence=min(0.99, base_confidence + agreement_bonus),
                evidence=evidence,
            )
        )
    return tuple(sorted(merged, key=lambda candidate: candidate.candidate_id))


def infer_mapping_candidates(
    source_terms: tuple[OntologyTerm, ...],
    target_terms: tuple[OntologyTerm, ...],
    *,
    synonym_groups: tuple[tuple[str, ...], ...] = (),
    source_vectors: dict[str, tuple[float, ...]] | None = None,
    target_vectors: dict[str, tuple[float, ...]] | None = None,
    embed_texts: Callable[[tuple[str, ...]], tuple[tuple[float, ...], ...]] | None = None,
    fuzzy_threshold: float = 0.84,
    structural_threshold: float = 0.5,
    embedding_threshold: float = 0.8,
) -> tuple[InferredMappingCandidate, ...]:
    """Run deterministic inference methods and merge duplicate candidates."""
    embedding_candidates: tuple[InferredMappingCandidate, ...] = ()
    if source_vectors is not None or target_vectors is not None or embed_texts is not None:
        embedding_candidates = infer_embedding_matches(
            source_terms,
            target_terms,
            source_vectors=source_vectors,
            target_vectors=target_vectors,
            embed_texts=embed_texts,
            threshold=embedding_threshold,
        )
    candidates = (
        *infer_exact_matches(source_terms, target_terms),
        *infer_fuzzy_matches(source_terms, target_terms, threshold=fuzzy_threshold),
        *infer_synonym_matches(source_terms, target_terms, synonym_groups=synonym_groups),
        *infer_structural_matches(source_terms, target_terms, threshold=structural_threshold),
        *embedding_candidates,
    )
    return merge_inferred_candidates(candidates)


def write_inferred_mapping_manifest(
    candidates: tuple[InferredMappingCandidate, ...],
    path: Path | str,
) -> Path:
    """Write a deterministic review queue for inferred mapping candidates."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "track_id": "track30_ontology_mapping_inference_20260625",
        "candidate_count": len(candidates),
        "candidates": [
            candidate.to_dict()
            for candidate in sorted(candidates, key=lambda item: item.candidate_id)
        ],
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def write_track30_inference_artifacts(output_dir: Path | str | None = None) -> dict[str, Path]:
    """Write deterministic Track 30 candidate and prompt artifacts."""
    root = Path(output_dir) if output_dir is not None else repo_root() / "data" / "ontologies"
    candidates = infer_mapping_candidates(
        _fixture_source_terms(),
        _fixture_target_terms(),
        synonym_groups=(("permission", "allowance", "authorization"),),
        source_vectors={"LKIF::permission": (1.0, 0.0), "LKIF::prohibition": (0.0, 1.0)},
        target_vectors={"ODRL::permission": (0.98, 0.02), "ODRL::prohibition": (0.02, 0.98)},
        structural_threshold=0.4,
        embedding_threshold=0.9,
    )
    return {
        INFERRED_MAPPING_MANIFEST_FILENAME: write_inferred_mapping_manifest(
            candidates,
            root / INFERRED_MAPPING_MANIFEST_FILENAME,
        ),
        LLM_INTERPRETATION_PROMPT_FILENAME: write_llm_interpretation_prompt(
            root / "inference_prompts" / LLM_INTERPRETATION_PROMPT_FILENAME,
        ),
    }


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[3]


def llm_interpretation_prompt_schema() -> dict[str, Any]:
    """Return the required structured output schema for optional LLM review."""
    return {
        "type": "object",
        "required": [
            "mapping_predicate",
            "confidence",
            "evidence",
            "review_status",
            "inferred",
            "reviewer_notes",
        ],
        "properties": {
            "mapping_predicate": {"enum": list(_STRONGEST_PREDICATES)},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "evidence": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "review_status": {"const": "needs_review"},
            "inferred": {"const": True},
            "reviewer_notes": {"type": "string"},
        },
        "additionalProperties": False,
    }


def write_llm_interpretation_prompt(path: Path | str) -> Path:
    """Write the optional LLM interpretation prompt contract to disk."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "task": "ontology_mapping_interpretation",
        "instruction": (
            "Compare the source and target ontology terms using only the supplied labels, "
            "definitions, hierarchy evidence, and provenance. Return JSON that conforms to "
            "the schema. Do not mark inferred mappings as authoritative."
        ),
        "required_output_schema": llm_interpretation_prompt_schema(),
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _best_similarity(source: OntologyTerm, target: OntologyTerm) -> tuple[float, str, str]:
    best = (0.0, "", "")
    for source_value in source.normalized_aliases:
        for target_value in target.normalized_aliases:
            score = _similarity(source_value, target_value)
            if score > best[0]:
                best = (score, source_value, target_value)
    return best


def _similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return max(
        SequenceMatcher(None, left, right).ratio(),
        _levenshtein_ratio(left, right),
        _jaro_winkler_similarity(left, right),
    )


def _levenshtein_ratio(left: str, right: str) -> float:
    distance = _levenshtein_distance(left, right)
    longest = max(len(left), len(right))
    if longest == 0:
        return 1.0
    return 1 - distance / longest


def _levenshtein_distance(left: str, right: str) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(
                min(
                    previous[right_index] + 1,
                    current[right_index - 1] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def _jaro_winkler_similarity(left: str, right: str) -> float:
    jaro = _jaro_similarity(left, right)
    prefix = 0
    for left_char, right_char in zip(left, right, strict=False):
        if left_char != right_char or prefix == 4:
            break
        prefix += 1
    return jaro + prefix * 0.1 * (1 - jaro)


def _jaro_similarity(left: str, right: str) -> float:
    if left == right:
        return 1.0
    if not left or not right:
        return 0.0
    match_distance = max(0, max(len(left), len(right)) // 2 - 1)
    left_matches = [False] * len(left)
    right_matches = [False] * len(right)
    matches = 0
    for left_index, left_char in enumerate(left):
        start = max(0, left_index - match_distance)
        end = min(left_index + match_distance + 1, len(right))
        for right_index in range(start, end):
            if right_matches[right_index] or left_char != right[right_index]:
                continue
            left_matches[left_index] = True
            right_matches[right_index] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    transpositions = 0
    right_index = 0
    for left_index, left_char in enumerate(left):
        if not left_matches[left_index]:
            continue
        while not right_matches[right_index]:
            right_index += 1
        if left_char != right[right_index]:
            transpositions += 1
        right_index += 1
    half_transpositions = transpositions / 2
    return (
        matches / len(left)
        + matches / len(right)
        + (matches - half_transpositions) / matches
    ) / 3


def _normalized_neighbourhood(term: OntologyTerm) -> frozenset[str]:
    return frozenset(
        normalize_mapping_text(value)
        for value in (*term.parents, *term.children)
        if normalize_mapping_text(value)
    )


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left.intersection(right)) / len(left.union(right))


def _resolve_term_vectors(
    terms: tuple[OntologyTerm, ...],
    vectors: dict[str, tuple[float, ...]] | None,
    embed_texts: Callable[[tuple[str, ...]], tuple[tuple[float, ...], ...]] | None,
) -> dict[str, tuple[float, ...]]:
    if vectors is not None:
        missing = [term.key for term in terms if term.key not in vectors]
        if missing:
            raise ValueError(f"missing embedding vectors for terms: {', '.join(missing)}")
        return vectors
    if embed_texts is None:
        raise ValueError("embedding inference requires vectors or an embed_texts callable")
    texts = tuple(_embedding_text(term) for term in terms)
    generated = embed_texts(texts)
    if len(generated) != len(terms):
        raise ValueError("embed_texts must return one vector per term")
    return {term.key: tuple(vector) for term, vector in zip(terms, generated, strict=True)}


def _embedding_text(term: OntologyTerm) -> str:
    return " ".join(part for part in (term.label, term.definition, *term.synonyms) if part.strip())


def _cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or not right or len(left) != len(right):
        raise ValueError("embedding vectors must be non-empty and share the same dimension")
    dot = sum(left_item * right_item for left_item, right_item in zip(left, right, strict=True))
    left_norm = sum(item * item for item in left) ** 0.5
    right_norm = sum(item * item for item in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _strongest_predicate(predicates: tuple[MappingPredicate, ...]) -> MappingPredicate:
    predicate_set = set(predicates)
    for predicate in _STRONGEST_PREDICATES:
        if predicate in predicate_set:
            return predicate
    return "skos:relatedMatch"


def _fixture_source_terms() -> tuple[OntologyTerm, ...]:
    return (
        OntologyTerm(
            "LKIF",
            "permission",
            "Permission",
            synonyms=("authorization",),
            parents=("legal effect",),
        ),
        OntologyTerm(
            "LKIF",
            "prohibition",
            "Prohibition",
            parents=("legal effect",),
        ),
    )


def _fixture_target_terms() -> tuple[OntologyTerm, ...]:
    return (
        OntologyTerm(
            "ODRL",
            "permission",
            "Permission",
            synonyms=("allowance",),
            parents=("policy rule", "legal effect"),
        ),
        OntologyTerm(
            "ODRL",
            "prohibition",
            "Prohibition",
            parents=("policy rule", "legal effect"),
        ),
    )


__all__ = [
    "INFERRED_MAPPING_MANIFEST_FILENAME",
    "LLM_INTERPRETATION_PROMPT_FILENAME",
    "InferenceMethod",
    "InferredMappingCandidate",
    "OntologyTerm",
    "infer_embedding_matches",
    "infer_exact_matches",
    "infer_fuzzy_matches",
    "infer_mapping_candidates",
    "infer_structural_matches",
    "infer_synonym_matches",
    "llm_interpretation_prompt_schema",
    "merge_inferred_candidates",
    "normalize_mapping_text",
    "repo_root",
    "slugify_mapping_token",
    "write_inferred_mapping_manifest",
    "write_llm_interpretation_prompt",
    "write_track30_inference_artifacts",
]
