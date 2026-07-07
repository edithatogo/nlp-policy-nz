"""Tests for cross-surface contract governance."""

from __future__ import annotations

from nlp_policy_nz.contract_governance import (
    build_conformance_matrix,
    build_contract_governance_report,
    detect_surface_gaps,
    release_checklist,
    write_contract_governance_artifacts,
)


def test_conformance_matrix_covers_all_surfaces() -> None:
    matrix = build_conformance_matrix()

    assert [row.surface for row in matrix] == ["cli", "api", "sdk", "report", "mcp"]
    assert matrix[0].status == "aligned"
    assert matrix[3].status == "interface_only"


def test_governance_report_is_json_ready() -> None:
    report = build_contract_governance_report()

    assert report["surface_count"] == 5
    assert report["matrix"][0]["surface"] == "cli"
    assert report["release_checklist"]
    assert "Refresh the CLI" in report["release_checklist"][0]


def test_detect_surface_gaps_flags_report_surface_only() -> None:
    gaps = detect_surface_gaps()

    assert any(gap["surface"] == "report" for gap in gaps)
    assert all(gap["status"] != "aligned" for gap in gaps)


def test_release_checklist_mentions_mirror_updates() -> None:
    checklist = release_checklist()

    assert any("GitHub issue mirror" in item for item in checklist)


def test_governance_artifacts_write(tmp_path) -> None:
    written = write_contract_governance_artifacts(tmp_path)

    assert written["contract_governance.json"].is_file()
    assert written["contract_governance.md"].is_file()
