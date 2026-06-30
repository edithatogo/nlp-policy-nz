from __future__ import annotations

import json
from pathlib import Path

TRACK28 = Path("conductor/tracks/archive/track28_ontology_discovery_intake_20260625")


def test_track28_conductor_registry_and_metadata_are_complete() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK28.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK28.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK28.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 28: Ontology Discovery and Intake (archived)" in registry
    assert str(TRACK28).replace("\\", "/") in registry
    assert metadata["track_id"] == "track28_ontology_discovery_intake_20260625"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK28.joinpath(required_file).is_file()


def test_track28_checked_in_artifacts_are_present_and_linked() -> None:
    evidence = TRACK28.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("data/ontologies/track28_discovery_log.json"),
        Path("data/ontologies/track28_triage.json"),
        Path("data/ontologies/track28_standards_registry_addendum.json"),
        Path("data/ontologies/track28_blockers.json"),
        Path("docs/ontology-discovery-intake.md"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    discovery = json.loads(required_artifacts[0].read_text(encoding="utf-8"))
    addendum = json.loads(required_artifacts[2].read_text(encoding="utf-8"))

    assert discovery["candidate_count"] >= 10
    assert addendum["extends_registry"] == "track26_standards_registry"
