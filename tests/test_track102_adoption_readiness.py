"""Validation tests for the Track 102 adoption-readiness gate."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _manifest():
    return json.loads((ROOT / "data/adoption_readiness.json").read_text(encoding="utf-8"))


def test_manifest_has_machine_checkable_claim_classes():
    manifest = _manifest()

    assert manifest["schema_version"] == "adoption-readiness.v1"
    assert set(manifest["claim_classes"]) == {"contract_only", "empirically_supported"}
    assert manifest["status"] == "blocked"


def test_manifest_links_all_coordinated_evidence_issues():
    issues = {issue for item in _manifest()["evidence"] for issue in item["issues"]}

    assert {129, 132, 133, 144} <= issues


def test_blocked_manifest_cannot_make_adoption_claims():
    manifest = _manifest()

    assert all(value == "not_ready" or value == "not_performed" for value in manifest["adoption_claims"].values())
    assert all(item["claim_class"] == "contract_only" for item in manifest["evidence"])
