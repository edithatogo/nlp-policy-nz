"""Track 25 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK25 = Path("conductor/archive/track25_ontology_coverage_audit_20260625")


def test_track25_conductor_artifacts_are_complete() -> None:
    """Track 25 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK25.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK25.joinpath("plan.md").read_text(encoding="utf-8")

    assert "## [x] Track 25: Ontology Coverage Audit for Existing Systems" not in registry
    assert str(TRACK25).replace("\\", "/") not in registry
    assert metadata["track_id"] == "track25_ontology_coverage_audit_20260625"
    assert metadata["status"] == "completed"
    assert "**Status**: Completed" in plan
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK25.joinpath(required_file).is_file()


def test_track25_evidence_links_checked_in_artifacts() -> None:
    """Track 25 evidence links the generated audit artifacts."""
    evidence = TRACK25.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("data/ontologies/coverage_manifest.json"),
        Path("data/ontologies/data_blocker_register.json"),
        Path("data/ontologies/ontology_implementation_backlog.json"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    manifest = json.loads(required_artifacts[0].read_text(encoding="utf-8"))
    blockers = json.loads(required_artifacts[1].read_text(encoding="utf-8"))
    backlog = json.loads(required_artifacts[2].read_text(encoding="utf-8"))

    assert manifest["audit_name"] == "track25_ontology_coverage_audit"
    assert manifest["summary"]["row_count"] == len(manifest["coverage_matrix"])
    assert len(blockers) > 0
    assert len(backlog) == len(blockers)
