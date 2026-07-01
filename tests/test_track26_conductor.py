"""Track 26 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK26 = Path("conductor/tracks/track26_ontology_standards_expansion_20260625")


def test_track26_conductor_artifacts_are_complete() -> None:
    """Track 26 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK26.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK26.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK26.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 26: Legislative and Parliamentary Ontology Standards Expansion" in registry
    assert str(TRACK26).replace("\\", "/") in registry
    assert metadata["track_id"] == "track26_ontology_standards_expansion_20260625"
    assert metadata["status"] == "completed"
    assert "**Status**: Completed" in plan
    assert "**Status**: Completed" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK26.joinpath(required_file).is_file()


def test_track26_evidence_links_checked_in_artifacts() -> None:
    """Track 26 evidence links the generated standards artifacts."""
    evidence = TRACK26.joinpath("evidence.md").read_text(encoding="utf-8")
    registry_path = Path("data/ontologies/track26_standards_registry.json")
    schema_path = Path("data/ontologies/standards_registry.schema.json")

    for artifact in (registry_path, schema_path):
        assert artifact.is_file()
        assert artifact.name in evidence

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert registry["registry_name"] == "track26_standards_registry"
    assert registry["summary"]["entry_count"] == len(registry["entries"])
    assert set(schema["required"]) <= set(registry)
    assert registry["summary"]["blocker_type_counts"]["none"] == 0
