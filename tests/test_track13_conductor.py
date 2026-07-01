"""Conductor contract tests for Track 13."""

from __future__ import annotations

import json
from pathlib import Path

TRACK13 = Path("conductor/tracks/archive/track13_argument_stance_20260613")


def test_track13_conductor_registry_and_metadata_are_complete() -> None:
    """Track 13 remains discoverable as an archived Conductor track."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK13.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK13.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK13.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 13: Argument Mining & Policy Stance Detection (archived)" in registry
    assert str(TRACK13).replace("\\", "/") in registry
    assert metadata["track_id"] == "track13_argument_stance_20260613"
    assert metadata["status"] == "archived"
    assert "**Status**: Archived" in plan
    assert "**Status**: Archived" in spec
    for required_file in (
        "index.md",
        "metadata.json",
        "plan.md",
        "spec.md",
        "evidence.md",
        "external_gate_manifest.json",
        "silver_label_manifest.json",
        "ai_provider_labelling_plan.json",
        "ontology_triangulation_manifest.json",
    ):
        assert TRACK13.joinpath(required_file).is_file()


def test_track13_evidence_keeps_external_gates_explicit() -> None:
    """Track 13 evidence must not treat silver or fixture labels as gold."""
    evidence = TRACK13.joinpath("evidence.md").read_text(encoding="utf-8")
    external_gates = json.loads(
        TRACK13.joinpath("external_gate_manifest.json").read_text(encoding="utf-8")
    )

    assert "500+ human/gold Hansard argument-component labels" in evidence
    assert "Silver labels remain silver evidence only" in evidence
    assert "accepted silver label count: 0" in evidence
    assert "conductor\\tracks\\track13_argument_stance_20260613" not in evidence
    assert {"human_label_set_min_500", "legalbert_heldout_eval"}.issubset(
        {gate["id"] for gate in external_gates["external_gates"]}
    )


def test_track13_archive_index_links_required_review_artifacts() -> None:
    """The archive index exposes every Track 13 review artifact."""
    index = TRACK13.joinpath("index.md").read_text(encoding="utf-8")

    for file_name in (
        "spec.md",
        "plan.md",
        "metadata.json",
        "evidence.md",
        "external_gate_manifest.json",
        "silver_label_manifest.json",
        "ai_provider_labelling_plan.json",
        "ontology_triangulation_manifest.json",
    ):
        assert file_name in index
