from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from nlp_policy_nz.extraction.hathi_ingestion import (
    AccessClass,
    AcquisitionMode,
    HathiArchiveItem,
    HathiRightsEvidence,
    PublicationDecision,
    RightsBasis,
)
from nlp_policy_nz.ocr.cloud_ops import (
    BudgetLimits,
    LedgerState,
    build_cloud_run_plan,
    enforce_dispatch_limits,
    quarantine_failed,
    retry_failed,
    transition_row,
    verify_signed_run_report,
    write_signed_run_report,
)


def _item(item_id: str, *, restricted: bool = False) -> HathiArchiveItem:
    access = AccessClass.RESTRICTED_METADATA if restricted else AccessClass.PUBLIC_FULL_TEXT
    return HathiArchiveItem(
        collection_id="hathi-nz",
        dataset_id="dataset-a",
        source_id=f"source-{item_id}",
        item_id=item_id,
        htid=f"htid-{item_id}",
        access_class=access,
        acquisition_mode=AcquisitionMode.GITHUB_ACTIONS,
        source_url=f"https://example.test/{item_id}",
        source_dataset_name="seed",
        rights_code="public" if not restricted else "restricted",
        digitization_profile="standard",
        publish_eligibility=(
            PublicationDecision.PUBLIC_FULL_TEXT
            if not restricted
            else PublicationDecision.METADATA_ONLY
        ),
        source_sha256=("a" * 64 if not restricted else None),
        rights_evidence=(
            HathiRightsEvidence(
                rights_basis=RightsBasis.HATHI_RIGHTS_PROFILE,
                authoritative_record_uri=f"https://rights.example.test/{item_id}",
                authoritative_snapshot_sha256="d" * 64,
                accessed_at=datetime(2026, 7, 19, tzinfo=UTC),
                territorial_applicability=("NZ",),
                may_acquire=True,
                may_process=True,
                may_publish_full_text=True,
                may_publish_derived_features=True,
            )
            if not restricted
            else None
        ),
    )


def test_cloud_plan_is_sharded_and_has_complete_rights_aware_ledger(tmp_path: Path) -> None:
    plan = build_cloud_run_plan(
        (_item("b"), _item("a"), _item("r", restricted=True)),
        run_id="run-1",
        pipeline_version="1.0.0",
        budget=BudgetLimits(max_cost_usd=10, max_concurrency=2, max_retries=2),
        shard_size=1,
    )

    assert [shard.item_ids for shard in plan.work_manifest.shards] == [("a",), ("b",), ("r",)]
    assert plan.ledger[-1].state is LedgerState.RESTRICTED
    report = write_signed_run_report(plan, tmp_path / "run-report.json", signing_key="test-key")
    assert json.loads(report.read_text(encoding="utf-8"))["content_sha256"]
    assert verify_signed_run_report(report, signing_key="test-key") is True


def test_transitions_retry_and_limits_fail_closed() -> None:
    plan = build_cloud_run_plan(
        (_item("a"),),
        run_id="run-1",
        pipeline_version="1.0.0",
        budget=BudgetLimits(max_cost_usd=1, max_concurrency=1, max_retries=1),
    )
    failed = transition_row(plan, "a", LedgerState.FAILED, error_code="worker_timeout")
    quarantined = quarantine_failed(failed)
    assert quarantined.quarantined_item_ids == ("a",)
    retried = retry_failed(failed)
    assert retried.ledger[0].state is LedgerState.PENDING
    with pytest.raises(ValueError, match="invalid ledger transition"):
        transition_row(plan, "a", LedgerState.PUBLISHED)
    with pytest.raises(ValueError, match="cost"):
        enforce_dispatch_limits(plan, estimated_cost_usd=2, active_workers=1)
    with pytest.raises(ValueError, match="concurrency"):
        enforce_dispatch_limits(plan, estimated_cost_usd=0, active_workers=2)
