"""Metadata-only contracts for secure cloud OCR orchestration."""

from __future__ import annotations

import hashlib
import hmac
import json
from enum import StrEnum
from pathlib import Path
from typing import Final, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from nlp_policy_nz.extraction.hathi_ingestion import (
    HathiArchiveItem,
    HathiWorkManifest,
    build_work_manifest,
)
from nlp_policy_nz.ocr.benchmark import BenchmarkResult


class LedgerState(StrEnum):
    """Allowed lifecycle states for one registry row."""

    PENDING = "pending"
    UNAVAILABLE = "unavailable"
    RESTRICTED = "restricted"
    PROCESSED = "processed"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    FAILED = "failed"


class BudgetLimits(BaseModel):
    """Hard run limits enforced before cloud work is dispatched."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_cost_usd: float = Field(ge=0)
    max_concurrency: int = Field(ge=1)
    max_retries: int = Field(ge=0)


class LedgerRow(BaseModel):
    """One metadata-only completeness ledger entry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str = Field(min_length=1)
    shard_id: str = Field(min_length=1)
    content_address: str = Field(min_length=1)
    state: LedgerState = LedgerState.PENDING
    attempts: int = Field(ge=0, default=0)
    output_digest: str | None = Field(default=None, pattern=r"^sha256:[0-9a-f]{64}$")
    error_code: str | None = None


class CloudRunPlan(BaseModel):
    """Resumable cloud plan containing identities and no corpus payload."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(pattern=r"^1\.0\.0$")
    run_id: str = Field(min_length=1)
    collection_id: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    work_manifest: HathiWorkManifest
    ledger: tuple[LedgerRow, ...]
    budget: BudgetLimits
    provenance: dict[str, str]
    quarantined_item_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_ledger(self) -> Self:
        """Require one ledger row for every planned work identity."""
        manifest_ids = {item.item_id for item in self.work_manifest.items}
        ledger_ids = {row.item_id for row in self.ledger}
        if manifest_ids != ledger_ids:
            raise ValueError("ledger must cover every work-manifest item exactly")
        if len(self.ledger) != len(ledger_ids):
            raise ValueError("ledger contains duplicate item ids")
        return self


class SignedRunReport(BaseModel):
    """Signed run summary suitable for artifact publication."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    status: str
    ledger_counts: dict[str, int]
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    signature: str = Field(pattern=r"^[0-9a-f]{64}$")


class DriftAlert(BaseModel):
    """Benchmark drift decision against a prior accepted result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: str
    baseline: float
    current: float
    relative_change: float
    drifted: bool


_TRANSITIONS: Final[dict[LedgerState, frozenset[LedgerState]]] = {
    LedgerState.PENDING: frozenset(
        {LedgerState.UNAVAILABLE, LedgerState.RESTRICTED, LedgerState.PROCESSED, LedgerState.FAILED}
    ),
    LedgerState.UNAVAILABLE: frozenset({LedgerState.PENDING, LedgerState.FAILED}),
    LedgerState.RESTRICTED: frozenset({LedgerState.REVIEWED, LedgerState.PUBLISHED}),
    LedgerState.PROCESSED: frozenset({LedgerState.REVIEWED, LedgerState.FAILED}),
    LedgerState.REVIEWED: frozenset({LedgerState.PUBLISHED, LedgerState.FAILED}),
    LedgerState.PUBLISHED: frozenset(),
    LedgerState.FAILED: frozenset({LedgerState.PENDING}),
}


def build_cloud_run_plan(
    items: tuple[HathiArchiveItem, ...],
    *,
    run_id: str,
    pipeline_version: str,
    budget: BudgetLimits,
    shard_size: int = 100,
) -> CloudRunPlan:
    """Build deterministic shards and a complete row-level ledger."""
    manifest = build_work_manifest(items, pipeline_version=pipeline_version, shard_size=shard_size)
    shard_by_item = {
        item_id: shard.shard_id for shard in manifest.shards for item_id in shard.item_ids
    }
    ledger = tuple(
        LedgerRow(
            item_id=item.item_id,
            shard_id=shard_by_item[item.item_id],
            content_address=item.content_address,
            state=LedgerState.RESTRICTED if not item.content_allowed else LedgerState.PENDING,
        )
        for item in manifest.items
    )
    return CloudRunPlan(
        schema_version="1.0.0",
        run_id=run_id,
        collection_id=manifest.collection_id,
        pipeline_version=pipeline_version,
        work_manifest=manifest,
        ledger=ledger,
        budget=budget,
        provenance={"payload_policy": "metadata_only", "orchestrator": "github_actions"},
    )


def transition_row(
    plan: CloudRunPlan,
    item_id: str,
    state: LedgerState,
    *,
    error_code: str | None = None,
    output_digest: str | None = None,
) -> CloudRunPlan:
    """Apply one fail-closed ledger transition."""
    rows = list(plan.ledger)
    for index, row in enumerate(rows):
        if row.item_id != item_id:
            continue
        if state not in _TRANSITIONS[row.state]:
            raise ValueError(f"invalid ledger transition: {row.state} -> {state}")
        attempts = row.attempts + (1 if state in {LedgerState.PROCESSED, LedgerState.FAILED} else 0)
        if attempts > plan.budget.max_retries + 1:
            raise ValueError("retry budget exceeded")
        rows[index] = row.model_copy(
            update={
                "state": state,
                "attempts": attempts,
                "error_code": error_code,
                "output_digest": output_digest,
            }
        )
        return plan.model_copy(update={"ledger": tuple(rows)})
    raise KeyError(f"unknown ledger item: {item_id}")


def retry_failed(plan: CloudRunPlan) -> CloudRunPlan:
    """Return failed rows to pending for an idempotent partial rerun."""
    result = plan
    for row in plan.ledger:
        if row.state is LedgerState.FAILED:
            result = transition_row(result, row.item_id, LedgerState.PENDING, error_code=None)
    return result


def quarantine_failed(plan: CloudRunPlan) -> CloudRunPlan:
    """Keep failed rows explicit while preventing accidental publication."""
    quarantined = tuple(sorted({*plan.quarantined_item_ids, *(row.item_id for row in plan.ledger if row.state is LedgerState.FAILED)}))
    return plan.model_copy(update={"quarantined_item_ids": quarantined})


def enforce_dispatch_limits(
    plan: CloudRunPlan, *, estimated_cost_usd: float, active_workers: int
) -> None:
    """Reject dispatches that exceed budget or concurrency controls."""
    if estimated_cost_usd > plan.budget.max_cost_usd:
        raise ValueError("estimated cloud cost exceeds run budget")
    if active_workers > plan.budget.max_concurrency:
        raise ValueError("active workers exceed concurrency limit")


def build_drift_alerts(
    baseline: BenchmarkResult, current: BenchmarkResult, *, threshold: float = 0.15
) -> tuple[DriftAlert, ...]:
    """Compare quality and operations metrics using a stable relative threshold."""
    metrics = ("character_error_rate", "word_error_rate", "cost_per_page_usd", "pages_per_second")
    alerts: list[DriftAlert] = []
    for metric in metrics:
        before = getattr(baseline, metric)
        after = getattr(current, metric)
        relative = (after - before) / before if before else (0.0 if after == 0 else 1.0)
        alerts.append(
            DriftAlert(
                metric=metric,
                baseline=before,
                current=after,
                relative_change=relative,
                drifted=abs(relative) >= threshold,
            )
        )
    return tuple(alerts)


def write_signed_run_report(plan: CloudRunPlan, path: Path | str, *, signing_key: str) -> Path:
    """Write an HMAC-signed completeness report without exposing payloads."""
    counts = {state.value: sum(row.state is state for row in plan.ledger) for state in LedgerState}
    status = (
        "failed"
        if counts[LedgerState.FAILED.value]
        else "in_progress"
        if counts[LedgerState.PENDING.value] or counts[LedgerState.PROCESSED.value]
        else "complete"
    )
    body = {
        "run_id": plan.run_id,
        "status": status,
        "ledger_counts": counts,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    signature = hmac.new(signing_key.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    report = SignedRunReport(**body, content_sha256=digest, signature=signature)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def verify_signed_run_report(path: Path | str, *, signing_key: str) -> bool:
    """Verify the report signature and its canonical content digest."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    signature = str(payload.pop("signature"))
    digest = str(payload.pop("content_sha256"))
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    expected_digest = hashlib.sha256(canonical).hexdigest()
    expected_signature = hmac.new(signing_key.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, expected_digest) and hmac.compare_digest(signature, expected_signature)


__all__ = [
    "BudgetLimits",
    "CloudRunPlan",
    "DriftAlert",
    "LedgerRow",
    "LedgerState",
    "SignedRunReport",
    "build_cloud_run_plan",
    "build_drift_alerts",
    "enforce_dispatch_limits",
    "quarantine_failed",
    "retry_failed",
    "transition_row",
    "verify_signed_run_report",
    "write_signed_run_report",
]
