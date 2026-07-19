"""Fail-closed empirical promotion evidence for FOI-O candidate lanes."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field


class FoioPromotionStatus(StrEnum):
    """Evidence status for one independently gated jurisdiction lane."""

    BLOCKED = "blocked"
    READY = "ready"


class FoioEvidenceSnapshot(BaseModel):
    """Immutable identities required for a promotion evidence run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    archive_repository: str = Field(min_length=1)
    archive_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    archive_content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    legal_source_revision: str = Field(pattern=r"^[0-9a-f]{40}$")
    ontology_version: str = Field(min_length=1)
    model_revision: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    rights_evidence_uri: str = Field(min_length=1)
    rights_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class FoioPromotionLane(BaseModel):
    """Owner-supplied evidence inputs and computed gate for one jurisdiction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    jurisdiction: Literal["NZ", "Cth", "NSW"]
    snapshot: FoioEvidenceSnapshot | None = None
    held_out_record_ids: tuple[str, ...] = ()
    training_record_ids: tuple[str, ...] = ()
    rights_cleared: bool = False
    reviewer_ids: tuple[str, ...] = ()
    adjudication_complete: bool = False
    evaluation_report: dict[str, Any] | None = None
    status: FoioPromotionStatus = FoioPromotionStatus.BLOCKED
    blockers: tuple[str, ...] = ()


class FoioPromotionEvidenceReport(BaseModel):
    """Deterministic report that never promotes a lane with missing evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "foio.promotion-evidence.v1"
    lanes: tuple[FoioPromotionLane, ...]

    @property
    def promotion_ready(self) -> bool:
        """Return whether every configured lane has passed every evidence gate."""
        return bool(self.lanes) and all(lane.status is FoioPromotionStatus.READY for lane in self.lanes)

    def to_dict(self) -> dict[str, Any]:
        """Return stable JSON-compatible report data."""
        return {
            "schema_version": self.schema_version,
            "promotion_ready": self.promotion_ready,
            "lanes": [lane.model_dump(mode="json") for lane in self.lanes],
        }


def assess_foio_promotion_lane(lane: FoioPromotionLane) -> FoioPromotionLane:
    """Compute the fail-closed evidence status for an owner-supplied lane."""
    blockers: list[str] = []
    if lane.snapshot is None:
        blockers.append("immutable source, legal, ontology, model, and rights identities are missing")
    else:
        for field_name in (
            "archive_revision",
            "archive_content_sha256",
            "legal_source_revision",
            "rights_snapshot_sha256",
        ):
            if _looks_placeholder(getattr(lane.snapshot, field_name)):
                blockers.append(f"{field_name} is a placeholder, not empirical evidence")
        if not lane.snapshot.rights_evidence_uri.startswith(("https://", "http://")):
            blockers.append("rights evidence URI is not a durable HTTP(S) reference")
    if not lane.held_out_record_ids:
        blockers.append("rights-cleared held-out record identifiers are missing")
    if set(lane.held_out_record_ids) & set(lane.training_record_ids):
        blockers.append("held-out and training record identifiers overlap")
    if not lane.rights_cleared:
        blockers.append("rights clearance for evaluation and derived metrics is not recorded")
    if not lane.reviewer_ids:
        blockers.append("reviewer identities are missing")
    if not lane.adjudication_complete:
        blockers.append("independent adjudication is incomplete")
    if lane.evaluation_report is None:
        blockers.append("held-out evaluation report is missing")
    status = FoioPromotionStatus.READY if not blockers else FoioPromotionStatus.BLOCKED
    return lane.model_copy(update={"status": status, "blockers": tuple(blockers)})


def build_foio_promotion_evidence_report(
    lanes: list[FoioPromotionLane] | tuple[FoioPromotionLane, ...],
) -> FoioPromotionEvidenceReport:
    """Assess lanes in jurisdiction order and return a deterministic report."""
    assessed = tuple(
        assess_foio_promotion_lane(lane)
        for lane in sorted(
            lanes,
            key=lambda item: (item.jurisdiction, item.snapshot.model_revision if item.snapshot else ""),
        )
    )
    return FoioPromotionEvidenceReport(lanes=assessed)


def load_foio_promotion_evidence_manifest(path: str | Path) -> FoioPromotionEvidenceReport:
    """Load a manifest and recompute its statuses rather than trusting JSON flags."""
    payload = orjson.loads(Path(path).read_bytes())
    lanes = tuple(FoioPromotionLane.model_validate(item) for item in payload.get("lanes", ()))
    return build_foio_promotion_evidence_report(lanes)


def render_foio_promotion_evidence_json(report: FoioPromotionEvidenceReport) -> str:
    """Render a stable machine-readable evidence report."""
    return orjson.dumps(report.to_dict(), option=orjson.OPT_SORT_KEYS).decode() + "\n"


def render_foio_promotion_evidence_markdown(report: FoioPromotionEvidenceReport) -> str:
    """Render concise human-readable blockers without exposing source content."""
    lines = [
        "# FOI-O Promotion Evidence",
        "",
        f"Promotion ready: `{str(report.promotion_ready).lower()}`",
        "",
        "| Jurisdiction | Status | Held-out records | Blockers |",
        "| --- | --- | ---: | --- |",
    ]
    for lane in report.lanes:
        blockers = "; ".join(lane.blockers) if lane.blockers else "none"
        lines.append(
            f"| {lane.jurisdiction} | {lane.status.value} | "
            f"{len(lane.held_out_record_ids)} | {blockers} |"
        )
    return "\n".join(lines) + "\n"


def _looks_placeholder(value: str) -> bool:
    """Reject obvious fixture placeholders without claiming to validate provenance."""
    return bool(re.fullmatch(r"([0-9a-f])\1+", value))
