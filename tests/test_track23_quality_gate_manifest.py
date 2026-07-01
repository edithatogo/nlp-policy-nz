from __future__ import annotations

import json
from pathlib import Path

TRACK23 = Path("conductor/tracks/track23_quality_infrastructure_20260613")
MANIFEST = TRACK23 / "external_gate_manifest.json"


def _manifest() -> dict[str, object]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_track23_full_quality_gates_are_explicit() -> None:
    manifest = _manifest()

    gates = {gate["id"]: gate for gate in manifest["gates"]}  # type: ignore[index]

    assert set(gates) == {
        "full_ruff_strict",
        "strict_basedpyright",
        "coverage_threshold",
        "full_quality_pass",
    }
    assert manifest["status"] == "complete"

    for gate in gates.values():
        assert gate["required"] is True
        assert gate["status"] == "satisfied"
        assert gate["command"]
        assert gate["accepted_artifacts"]
        assert gate["required_evidence_fields"]
        assert gate["completion_criteria"]


def test_track23_manifest_rejects_focused_checks_as_surrogates() -> None:
    manifest = _manifest()
    rule = manifest["non_surrogate_rule"]

    assert isinstance(rule, str)
    for phrase in (
        "Focused tests",
        "scoped Ruff runs",
        "scaffold checks",
        "configuration inspection",
        "not accepted as substitutes",
    ):
        assert phrase in rule


def test_track23_coverage_gate_declares_threshold() -> None:
    gates = {gate["id"]: gate for gate in _manifest()["gates"]}  # type: ignore[index]
    coverage_gate = gates["coverage_threshold"]

    assert coverage_gate["minimum_coverage_percent"] == 90.0
    assert "artifacts/track23/coverage_20260701.json" in coverage_gate["accepted_artifacts"]
    assert "coverage_percent" in coverage_gate["required_evidence_fields"]
    assert "minimum_coverage_percent" in coverage_gate["required_evidence_fields"]


def test_track23_mutation_gate_remains_satisfied_but_not_a_quality_surrogate() -> None:
    manifest = _manifest()
    satisfied = {gate["id"]: gate for gate in manifest["already_satisfied"]}  # type: ignore[index]

    assert satisfied["mutation_ci_gate"]["status"] == "satisfied"
    assert "mutation_ci_gate" not in {
        gate["id"]
        for gate in manifest["gates"]  # type: ignore[index]
    }
