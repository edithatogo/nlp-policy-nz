"""Tests for the Track 76 source inventory helpers."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import polars as pl

from nlp_policy_nz.extraction.source_inventory import (
    default_source_inventory_manifest,
    detect_source_inventory_live_probe_report,
    render_source_inventory_json,
    render_source_inventory_markdown,
    validate_source_inventory_manifest,
    write_source_inventory_artifacts,
    write_source_inventory_parquet,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK76_DIR = ROOT / "data" / "track76"


def test_default_source_inventory_manifest_covers_required_statuses() -> None:
    """The default manifest should cover each required source-status bucket."""
    manifest = default_source_inventory_manifest()

    assert manifest.schema_version == "1.0"
    assert manifest.summary.total_records == 7
    assert manifest.summary.available_records == 2
    assert manifest.summary.status_counts["available"] == 2
    assert manifest.summary.status_counts["redirected"] == 1
    assert manifest.summary.status_counts["pdf_only"] == 1
    assert manifest.summary.status_counts["malformed"] == 1
    assert manifest.summary.status_counts["access_blocked"] == 1
    assert manifest.summary.status_counts["unavailable"] == 1
    assert manifest.summary.known_gap_count == 5
    assert "fixture-bounded" in manifest.claim_boundary
    assert "whole-corpus readiness" in manifest.claim_boundary

    available = next(record for record in manifest.records if record.status == "available")
    assert available.checksum_sha256 is not None
    assert len(available.checksum_sha256) == 64
    assert available.rights_note is not None
    assert available.update_policy == "refresh-on-change"


def test_source_inventory_manifest_validation_rejects_missing_checksum_and_duplicate_ids() -> None:
    """Inventory validation should fail closed on malformed source records."""
    manifest = default_source_inventory_manifest()
    broken_record = replace(manifest.records[0], checksum_sha256=None)
    duplicate_manifest = replace(manifest, records=(broken_record, *manifest.records[1:]))

    valid, errors = validate_source_inventory_manifest(duplicate_manifest)

    assert valid is False
    assert any("missing checksum" in error for error in errors)

    duplicate_id_record = replace(manifest.records[1], inventory_id=manifest.records[0].inventory_id)
    duplicate_id_manifest = replace(
        manifest, records=(manifest.records[0], duplicate_id_record, *manifest.records[2:])
    )

    valid, errors = validate_source_inventory_manifest(duplicate_id_manifest)

    assert valid is False
    assert any("duplicate inventory id" in error for error in errors)


def test_source_inventory_live_probe_reports_ci_and_windows_skips() -> None:
    """Optional live probes should skip cleanly on CI and Windows."""
    ci_report = detect_source_inventory_live_probe_report(
        include_live_probe=True,
        platform_name="Linux",
        ci=True,
    )
    windows_report = detect_source_inventory_live_probe_report(
        include_live_probe=True,
        platform_name="Windows",
        ci=False,
    )

    assert ci_report.status == "skipped"
    assert "GitHub Actions" in ci_report.skip_reason
    assert windows_report.status == "skipped"
    assert "Windows" in windows_report.skip_reason


def test_source_inventory_renderers_match_committed_artifacts() -> None:
    """The committed inventory artifacts should match the deterministic renderers."""
    manifest = default_source_inventory_manifest()

    assert (TRACK76_DIR / "source_inventory.json").read_text(encoding="utf-8") == (
        render_source_inventory_json(manifest)
    )
    assert (TRACK76_DIR / "source_inventory.md").read_text(encoding="utf-8") == (
        render_source_inventory_markdown(manifest)
    )

    payload = json.loads(render_source_inventory_json(manifest))
    assert payload["summary"]["total_records"] == 7
    assert payload["summary"]["known_gap_count"] == 5


def test_source_inventory_parquet_round_trip(tmp_path: Path) -> None:
    """The inventory should be exportable as a deterministic Parquet table."""
    manifest = default_source_inventory_manifest()
    output = tmp_path / "source_inventory.parquet"

    written = write_source_inventory_parquet(output, manifest)
    table = pl.read_parquet(written)

    assert written == output
    assert table.height == 7
    assert set(table["status"]) == {
        "access_blocked",
        "available",
        "malformed",
        "pdf_only",
        "redirected",
        "unavailable",
    }


def test_source_inventory_artifact_bundle_writes_expected_files(tmp_path: Path) -> None:
    """The artifact writer should emit the JSON, markdown, and Parquet outputs together."""
    written = write_source_inventory_artifacts(tmp_path)

    assert (tmp_path / "source_inventory.json").is_file()
    assert (tmp_path / "source_inventory.md").is_file()
    assert (tmp_path / "source_inventory.parquet").is_file()
    assert written["source_inventory.json"] == tmp_path / "source_inventory.json"
    assert written["source_inventory.md"] == tmp_path / "source_inventory.md"
    assert written["source_inventory.parquet"] == tmp_path / "source_inventory.parquet"
