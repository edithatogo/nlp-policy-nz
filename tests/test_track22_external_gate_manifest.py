"""Track 22 external Isaacus integration gate manifest checks."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(
    "conductor/archive/track22_isaacus_integration_20260613/"
    "external_gate_manifest.json"
)


def test_track22_external_gate_manifest_is_explicit() -> None:
    """Track 22 should separate repo-side scaffolding from live Isaacus gates."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["track"] == 22
    assert manifest["status"] == "externally_blocked"
    assert manifest["repo_side_status"] == "complete"
    observations = manifest["local_runtime_observations"]
    assert observations["audit_wrappers_only"] is True
    assert observations["network_download_started"] is False
    assert observations["proprietary_api_started"] is False
    assert observations["measured_retrieval_claimed"] is False

    gates = {gate["id"]: gate for gate in manifest["external_gates"]}
    assert (
        gates["open_australian_legal_corpus_integration"]["minimum_records"]
        >= 147_000
    )
    assert gates["isaacus_model_evaluation"]["minimum_models"] >= 3
    assert gates["nz_mleb_publication"]["minimum_queries"] >= 3
    assert "credentialed API" in gates["kanon_2_retrieval_evaluation"]["notes"]

    validation_commands = {
        check["name"]: check["command"] for check in manifest["local_validation"]
    }
    assert validation_commands["manifest validation"] == (
        "pixi run python -m json.tool "
        "conductor/archive/track22_isaacus_integration_20260613/"
        "external_gate_manifest.json"
    )


def test_track22_external_gate_manifest_rejects_surrogates() -> None:
    """Offline manifests and fixtures must not satisfy live Isaacus gates."""
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()

    for rejected in (
        "offline manifests",
        "local fixtures",
        "audit wrappers",
        "mock api responses",
        "fixture metrics",
        "unpublished benchmark reports",
        "mock hub publication",
    ):
        assert rejected in manifest_text
