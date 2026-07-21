"""Executable Track 132 intake contract tests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from scripts.validate_track132_intake import report, validate

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "track132"


def _payloads() -> tuple[dict, dict, dict]:
    return tuple(json.loads(path.read_text(encoding="utf-8")) for path in (
        BASE / "intake_contract.json", BASE / "intake_manifest.json", BASE / "evaluation_inputs.json"
    ))  # type: ignore[return-value]


def _complete_payloads() -> tuple[dict, dict, dict]:
    contract, manifest, evaluation = _payloads()
    digest = "a" * 64
    manifest["people"] = [
        {"person_id": "ann-1", "role": "annotator", "identity_evidence_ref": "vault:ann-1"},
        {"person_id": "adj-1", "role": "adjudicator", "identity_evidence_ref": "vault:adj-1"},
    ]
    manifest["authority_records"] = [{
        "authority_id": "auth-1", "subject_id": "person-1", "authority_type": "role",
        "valid_from": "1900-01-01", "valid_to": "1900-12-31", "source_uri": "https://example.invalid/auth-1",
        "evidence_sha256": digest,
    }]
    manifest["review_decisions"] = [{
        "decision_id": "review-1", "record_id": "test-1", "adjudicator_id": "adj-1",
        "decision": "accepted", "signed_at": "1900-06-02T00:00:00Z", "signature_ref": "vault:sig-1",
        "signature_sha256": digest,
    }]
    manifest["records"] = [{
        "record_id": "test-1", "source_id": "source-1", "volume_id": "volume-1", "page_id": "page-1",
        "event_date": "1900-06-01", "split": "test", "source_sha256": digest,
        "annotation_ref": "vault:annotation-1", "annotator_ids": ["ann-1"], "adjudicator_ids": ["adj-1"],
        "authority_record_ids": ["auth-1"], "review_decision_id": "review-1",
    }]
    evaluation["metrics"] = dict.fromkeys(contract["required_metrics"], 1.0)
    return contract, manifest, evaluation


def test_empty_scaffold_is_valid_but_no_promotion() -> None:
    contract, manifest, evaluation = _payloads()
    errors = validate(contract, manifest, evaluation)
    result = report(contract, manifest, evaluation, errors)

    assert errors == []
    assert result["promotion_ready"] is False
    assert result["decision"] == "no-promotion"
    assert "no held-out test records are present" in result["reasons"]


def test_complete_evidence_can_promote_only_at_declared_thresholds() -> None:
    contract, manifest, evaluation = _complete_payloads()
    errors = validate(contract, manifest, evaluation)
    assert errors == []
    assert report(contract, manifest, evaluation, errors)["decision"] == "promote"

    changed = copy.deepcopy(evaluation)
    changed["metrics"]["speaker_accuracy"] = 0.1
    assert "metric below threshold: speaker_accuracy" in validate(contract, manifest, changed)


def test_temporal_authority_and_signed_review_are_fail_closed() -> None:
    contract, manifest, evaluation = _complete_payloads()
    manifest["authority_records"][0]["valid_to"] = "1899-12-31"
    manifest["review_decisions"][0]["signature_sha256"] = "missing"
    errors = validate(contract, manifest, evaluation)

    assert "authority validity does not cover record event_date: test-1" in errors
    assert "review review-1 has invalid signature_sha256" in errors


def test_cli_writes_deterministic_fail_closed_report() -> None:
    output = ROOT / ".tmp" / "track132-test-report.json"
    result = subprocess.run(
        [sys.executable, "scripts/validate_track132_intake.py", "--output", str(output)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert json.loads(output.read_text(encoding="utf-8"))["decision"] == "no-promotion"
