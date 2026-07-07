"""Fail-closed RuleSpec promotion contracts for reviewed RAC handoff artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

from nlp_policy_nz.axiom.rulespec import RuleSpecReference
from nlp_policy_nz.extraction.schemas import ExtractedSpan, SourceTrace

RULESPEC_HANDOFF_JSON = "rulespec_promotion_handoff.json"
RULESPEC_HANDOFF_YAML = "rulespec_promotion_handoff.yaml"


class PromotionState(StrEnum):
    """Review states for RuleSpec promotion candidates."""

    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    BLOCKED = "blocked"
    PROMOTED = "promoted"


@dataclass(frozen=True)
class RuleSpecOracleFixtureRef:
    """Pointer to a deterministic oracle fixture consumed by downstream runtimes."""

    fixture_id: str
    path: str
    description: str | None = None

    def __post_init__(self) -> None:
        """Validate the oracle fixture reference."""
        _require_nonempty("fixture_id", self.fixture_id)
        _require_nonempty("path", self.path)

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON/YAML-compatible mapping."""
        return asdict(self)


@dataclass(frozen=True)
class RuleSpecReviewerEvidence:
    """Reviewer evidence that justifies promotion, rejection, or deferment."""

    reviewer: str
    reviewed_at: str
    evidence_uri: str
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate the reviewer evidence reference."""
        _require_nonempty("reviewer", self.reviewer)
        _require_nonempty("reviewed_at", self.reviewed_at)
        _require_nonempty("evidence_uri", self.evidence_uri)

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON/YAML-compatible mapping."""
        return asdict(self)


@dataclass(frozen=True)
class RuleSpecFormula:
    """Reviewed or pending executable formula metadata."""

    formula_id: str
    status: PromotionState
    expression: str
    entity: str
    period: str
    parameters: tuple[str, ...] = field(default_factory=tuple)
    source_spans: tuple[ExtractedSpan, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        """Validate reviewed formula identity and normalise its status."""
        _require_nonempty("formula_id", self.formula_id)
        _require_nonempty("expression", self.expression)
        _require_nonempty("entity", self.entity)
        _require_nonempty("period", self.period)
        object.__setattr__(self, "status", _normalize_state(self.status))
        object.__setattr__(self, "parameters", tuple(_require_nonempty("parameter", p) for p in self.parameters))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON/YAML-compatible mapping."""
        return {
            "formula_id": self.formula_id,
            "status": self.status.value,
            "expression": self.expression,
            "entity": self.entity,
            "period": self.period,
            "parameters": list(self.parameters),
            "source_spans": [span.model_dump() for span in self.source_spans],
        }


@dataclass(frozen=True)
class RuleSpecPromotionHandoff:
    """Offline RuleSpec promotion payload with fail-closed review gating."""

    rulespec_reference: RuleSpecReference
    review_state: PromotionState
    source_trace: SourceTrace
    source_verification: dict[str, Any]
    legal_effect: str | None
    entities: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    periods: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    parameters: dict[str, Any] = field(default_factory=dict)
    formulas: tuple[RuleSpecFormula, ...] = field(default_factory=tuple)
    oracle_fixture_refs: tuple[RuleSpecOracleFixtureRef, ...] = field(default_factory=tuple)
    reviewer_evidence: tuple[RuleSpecReviewerEvidence, ...] = field(default_factory=tuple)
    review_notes: str | None = None
    rejection_reason: str | None = None
    defer_reason: str | None = None
    downstream_targets: tuple[str, ...] = ("rulespec-nz", "policyengine", "openfisca")

    def __post_init__(self) -> None:
        """Normalise the promotion payload and enforce fail-closed review gates."""
        object.__setattr__(self, "review_state", _normalize_state(self.review_state))
        object.__setattr__(self, "entities", _normalize_mapping_tuple("entity", self.entities))
        object.__setattr__(self, "periods", _normalize_mapping_tuple("period", self.periods))
        object.__setattr__(self, "parameters", _normalize_mapping("parameter", self.parameters))
        object.__setattr__(self, "downstream_targets", tuple(_require_nonempty("target", target) for target in self.downstream_targets))
        _validate_source_trace(self.source_trace)
        _validate_source_verification(self.source_verification)
        _validate_review_state_fields(self)

    @property
    def rulespec_id(self) -> str:
        """Return the durable RuleSpec identifier."""
        return self.rulespec_reference.durable_id

    def is_promotable(self) -> bool:
        """Return whether the handoff passes the promotion gate."""
        try:
            validate_rulespec_promotion_handoff(self)
        except ValueError:
            return False
        return self.review_state == PromotionState.PROMOTED

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON/YAML-compatible handoff payload."""
        return {
            "rulespec_reference": self.rulespec_reference.to_dict(),
            "rulespec_id": self.rulespec_id,
            "review_state": self.review_state.value,
            "source_trace": self.source_trace.model_dump(),
            "source_verification": dict(self.source_verification),
            "legal_effect": self.legal_effect,
            "entities": [dict(item) for item in self.entities],
            "periods": [dict(item) for item in self.periods],
            "parameters": dict(self.parameters),
            "formulas": [formula.to_dict() for formula in self.formulas],
            "oracle_fixture_refs": [fixture.to_dict() for fixture in self.oracle_fixture_refs],
            "reviewer_evidence": [evidence.to_dict() for evidence in self.reviewer_evidence],
            "review_notes": self.review_notes,
            "rejection_reason": self.rejection_reason,
            "defer_reason": self.defer_reason,
            "downstream_targets": list(self.downstream_targets),
        }


def build_rulespec_promotion_handoff(
    bridge_record: object,
    *,
    source_trace: SourceTrace,
    review_state: PromotionState | str = PromotionState.CANDIDATE,
    entities: tuple[dict[str, Any], ...] = (),
    periods: tuple[dict[str, Any], ...] = (),
    parameters: dict[str, Any] | None = None,
    formulas: tuple[RuleSpecFormula, ...] = (),
    oracle_fixture_refs: tuple[RuleSpecOracleFixtureRef, ...] = (),
    reviewer_evidence: tuple[RuleSpecReviewerEvidence, ...] = (),
    review_notes: str | None = None,
    rejection_reason: str | None = None,
    defer_reason: str | None = None,
) -> RuleSpecPromotionHandoff:
    """Build a handoff payload from a bridge record and source trace."""
    rulespec = getattr(bridge_record, "rulespec", None)
    if not isinstance(rulespec, dict):
        raise ValueError("bridge record must include rulespec metadata")
    rulespec_reference = _rulespec_reference_from_rulespec(rulespec)
    source_verification = _source_verification_from_bridge(bridge_record, source_trace)
    legal_effect = getattr(getattr(bridge_record, "norm_semantics", None), "legal_effect", None)
    return RuleSpecPromotionHandoff(
        rulespec_reference=rulespec_reference,
        review_state=_normalize_state(review_state),
        source_trace=source_trace,
        source_verification=source_verification,
        legal_effect=legal_effect,
        entities=entities,
        periods=periods,
        parameters=parameters or {},
        formulas=formulas,
        oracle_fixture_refs=oracle_fixture_refs,
        reviewer_evidence=reviewer_evidence,
        review_notes=review_notes,
        rejection_reason=rejection_reason,
        defer_reason=defer_reason,
    )


def validate_rulespec_promotion_handoff(handoff: RuleSpecPromotionHandoff) -> None:
    """Raise if a handoff is not promotable or is structurally incomplete."""
    errors: list[str] = []
    if not handoff.source_trace.spans:
        errors.append("source spans are required")
    if handoff.review_state in {PromotionState.REVIEWED, PromotionState.PROMOTED, PromotionState.REJECTED, PromotionState.DEFERRED, PromotionState.BLOCKED} and not handoff.reviewer_evidence:
        errors.append("legal review evidence is required")
    if handoff.review_state == PromotionState.PROMOTED:
        if not handoff.oracle_fixture_refs:
            errors.append("oracle fixture references are required for promotion")
        if not handoff.formulas:
            errors.append("at least one formula is required for promotion")
        elif any(formula.status != PromotionState.REVIEWED for formula in handoff.formulas):
            errors.append("formula status must be reviewed before promotion")
    if handoff.review_state == PromotionState.REJECTED and not handoff.rejection_reason:
        errors.append("rejection_reason is required for rejected handoffs")
    if handoff.review_state in {PromotionState.DEFERRED, PromotionState.BLOCKED} and not (
        handoff.defer_reason or handoff.review_notes
    ):
        errors.append("defer_reason or review_notes is required for deferred or blocked handoffs")
    if errors:
        raise ValueError("; ".join(errors))


def render_rulespec_promotion_handoff_json(handoff: RuleSpecPromotionHandoff) -> str:
    """Render a handoff payload as stable formatted JSON."""
    return json.dumps(handoff.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_rulespec_promotion_handoff_yaml(handoff: RuleSpecPromotionHandoff) -> str:
    """Render a handoff payload as stable YAML."""
    return yaml.safe_dump(handoff.to_dict(), sort_keys=True, allow_unicode=True)


def write_rulespec_promotion_handoff(
    handoff: RuleSpecPromotionHandoff,
    output_dir: str | Path,
) -> tuple[Path, Path]:
    """Write JSON/YAML handoff artifacts and return their paths."""
    validate_rulespec_promotion_handoff(handoff)
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / RULESPEC_HANDOFF_JSON
    yaml_path = root / RULESPEC_HANDOFF_YAML
    json_path.write_text(render_rulespec_promotion_handoff_json(handoff), encoding="utf-8")
    yaml_path.write_text(render_rulespec_promotion_handoff_yaml(handoff), encoding="utf-8")
    return json_path, yaml_path


def _rulespec_reference_from_rulespec(rulespec: dict[str, Any]) -> RuleSpecReference:
    reference = rulespec.get("rulespec_reference")
    if not isinstance(reference, dict):
        raise ValueError("rulespec.rulespec_reference is required")
    return RuleSpecReference(
        jurisdiction=str(reference.get("jurisdiction") or "nz"),
        path=str(reference.get("path") or ""),
        concept=str(reference.get("concept") or ""),
    )


def _source_verification_from_bridge(bridge_record: object, source_trace: SourceTrace) -> dict[str, Any]:
    source_anchor = getattr(bridge_record, "source_anchor", None)
    rulespec = getattr(bridge_record, "rulespec", {})
    module = rulespec.get("module", {}) if isinstance(rulespec, dict) else {}
    verification = module.get("source_verification", {}) if isinstance(module, dict) else {}
    return {
        "corpus_citation_path": verification.get("corpus_citation_path", source_trace.citation_path),
        "jurisdiction": verification.get("jurisdiction", getattr(source_anchor, "jurisdiction", "NZ")),
        "document_type": verification.get("document_type", getattr(source_anchor, "document_type", "act")),
        "authoritative_source_url": getattr(
            source_anchor,
            "source_url",
            verification.get("authoritative_source_url"),
        ),
        "retrieved_at": source_trace.retrieved_at,
        "source_sha256": getattr(source_anchor, "source_sha256", source_trace.source_sha256),
    }


def _validate_source_trace(source_trace: SourceTrace) -> None:
    if not source_trace.spans:
        raise ValueError("source spans are required")


def _validate_source_verification(source_verification: dict[str, Any]) -> None:
    for field_name in ("corpus_citation_path", "jurisdiction", "document_type", "authoritative_source_url", "retrieved_at", "source_sha256"):
        value = source_verification.get(field_name)
        _require_nonempty(field_name, "" if value is None else str(value))


def _validate_review_state_fields(handoff: RuleSpecPromotionHandoff) -> None:
    if handoff.review_state == PromotionState.REVIEWED and not handoff.reviewer_evidence:
        raise ValueError("legal review evidence is required")
    if handoff.review_state == PromotionState.PROMOTED:
        validate_rulespec_promotion_handoff(handoff)


def _normalize_state(value: PromotionState | str) -> PromotionState:
    if isinstance(value, PromotionState):
        return value
    normalized = _require_nonempty("review_state", value).replace("-", "_").lower()
    try:
        return PromotionState(normalized)
    except ValueError as exc:
        allowed = ", ".join(state.value for state in PromotionState)
        msg = f"review_state must be one of: {allowed}"
        raise ValueError(msg) from exc


def _normalize_mapping(name: str, value: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, item in value.items():
        key_str = _require_nonempty(f"{name} key", str(key))
        normalized[key_str] = item
    return normalized


def _normalize_mapping_tuple(name: str, values: tuple[dict[str, Any], ...]) -> tuple[dict[str, Any], ...]:
    return tuple(_normalize_mapping(name, value) for value in values)


def _require_nonempty(name: str, value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} is required")
    return stripped
