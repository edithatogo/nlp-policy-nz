"""Track 20 external model-training gate manifest checks."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path("conductor/archive/track20_legal_finetuning_20260613/external_gate_manifest.json")


def test_track20_external_gate_manifest_is_explicit() -> None:
    """Track 20 should separate repo-side completion from model-quality gates."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["track"] == 20
    assert manifest["status"] == "externally_blocked"
    assert manifest["repo_side_status"] == "complete"
    assert manifest["local_runtime_observations"]["selected_ci_backend"] == "ci_cpu"
    assert manifest["local_runtime_observations"]["full_scale_training_claimed"] is False

    gates = {gate["id"]: gate for gate in manifest["external_gates"]}
    assert gates["legal_bert_mlm_training"]["minimum_training_steps"] >= 100_000
    assert gates["tier2_qlora_training"]["minimum_models"] >= 3
    assert gates["held_out_quality_evaluation"]["minimum_citation_f1_improvement"] >= 0.10
    assert gates["hugging_face_model_publication"]["namespace"] == "nlp-policy-nz"
    validation_commands = {
        check["name"]: check["command"] for check in manifest["local_validation"]
    }
    assert validation_commands["manifest validation"] == (
        "pixi run python -m json.tool "
        "conductor/archive/track20_legal_finetuning_20260613/"
        "external_gate_manifest.json"
    )


def test_track20_external_gate_manifest_rejects_surrogates() -> None:
    """Dry-run and smoke evidence must not satisfy production-training gates."""
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()

    for rejected in (
        "dry-run specs",
        "cpu smoke tests",
        "fixture metrics",
        "synthetic labels",
        "mock hub publication",
        "untrained model cards",
    ):
        assert rejected in manifest_text
