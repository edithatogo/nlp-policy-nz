"""Track 21 external architecture-gate manifest checks."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(
    "conductor/tracks/track21_bleeding_edge_architectures_20260613/"
    "external_gate_manifest.json"
)


def test_track21_external_gate_manifest_is_explicit() -> None:
    """Track 21 should separate repo-side completion from live model gates."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["track"] == 21
    assert manifest["status"] == "externally_blocked"
    assert manifest["repo_side_status"] == "complete"
    observations = manifest["local_runtime_observations"]
    assert observations["audit_wrappers_only"] is True
    assert observations["model_download_started"] is False
    assert observations["live_training_started"] is False
    assert observations["measured_pareto_claimed"] is False

    gates = {gate["id"]: gate for gate in manifest["external_gates"]}
    assert gates["third_party_architecture_setup"]["minimum_architectures"] >= 3
    assert gates["measured_nz_legal_benchmark"]["minimum_architectures"] >= 3
    assert gates["measured_nz_legal_benchmark"]["minimum_context_tokens"] >= 50_000
    assert gates["hugging_face_evaluation_publication"]["namespace"] == "nlp-policy-nz"

    validation_commands = {
        check["name"]: check["command"] for check in manifest["local_validation"]
    }
    assert validation_commands["manifest validation"] == (
        "pixi run python -m json.tool "
        "conductor/tracks/track21_bleeding_edge_architectures_20260613/"
        "external_gate_manifest.json"
    )


def test_track21_external_gate_manifest_rejects_surrogates() -> None:
    """Dry-run architecture evidence must not satisfy live benchmark gates."""
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()

    for rejected in (
        "audit wrappers",
        "deterministic example metrics",
        "dry-run reports",
        "fixture metrics",
        "unpublished checkpoint manifests",
        "mock hub publication",
    ):
        assert rejected in manifest_text
