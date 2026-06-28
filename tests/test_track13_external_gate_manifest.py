"""Track 13 external evidence gate manifest checks."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(
    "conductor/tracks/archive/track13_argument_stance_20260613/"
    "external_gate_manifest.json"
)


def test_track13_external_gate_manifest_is_explicit() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["track"] == 13
    assert manifest["status"] == "externally_blocked"
    assert manifest["repo_side_status"] == "complete"

    gates = {gate["id"]: gate for gate in manifest["external_gates"]}
    assert gates["human_label_set_min_500"]["minimum_count"] >= 500
    assert "annotator_id" in gates["human_label_set_min_500"]["required_fields"]
    assert "heldout_f1_macro" in gates["legalbert_heldout_eval"]["required_metrics"]

    silver_gate = manifest["silver_alternative_gates"][0]
    assert silver_gate["id"] == "silver_argument_label_set"
    assert silver_gate["status"] == "accepted_alternative"
    assert silver_gate["requires_human_labelled_calibration_source"] is True
    assert "gold human-label" in silver_gate["notes"]


def test_track13_external_gate_manifest_rejects_surrogates() -> None:
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()

    for rejected in (
        "ai-generated labels",
        "heuristic labels",
        "synthetic labels",
        "mock",
        "rule-based",
    ):
        assert rejected in manifest_text
