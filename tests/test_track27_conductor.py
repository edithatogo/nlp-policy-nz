"""Track 27 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK27 = Path("conductor/archive/track27_rules_as_code_semantic_bridge_20260625")


def test_track27_conductor_artifacts_are_complete() -> None:
    """Track 27 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK27.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK27.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK27.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 27: Rules-as-Code Semantic Bridge" not in registry
    assert str(TRACK27).replace("\\", "/") not in registry
    assert metadata["track_id"] == "track27_rules_as_code_semantic_bridge_20260625"
    assert metadata["status"] == "completed"
    assert "**Status**: Completed" in plan
    assert "**Status**: Completed" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK27.joinpath(required_file).is_file()


def test_track27_evidence_records_bridge_and_external_gate() -> None:
    """Track 27 evidence records the implemented bridge and live parity gate."""
    evidence = TRACK27.joinpath("evidence.md").read_text(encoding="utf-8")

    for expected in (
        "src/nlp_policy_nz/ontology/rac_bridge.py",
        "nlp-policy-nz rac-export",
        "tests/test_rac_bridge.py",
        "RuleSpec",
        "PROV-O",
        "schema.org/Legislation",
        "OpenFisca",
        "PolicyEngine",
        "NotImplementedError",
        "oracle fixtures",
    ):
        assert expected in evidence
