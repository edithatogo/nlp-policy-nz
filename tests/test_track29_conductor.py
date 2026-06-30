from __future__ import annotations

import json
from pathlib import Path

TRACK29 = Path("conductor/tracks/archive/track29_ontology_mapping_kg_20260625")


def test_track29_conductor_registry_and_metadata_are_complete() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK29.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK29.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK29.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 29: Ontology Mapping Knowledge Graph (archived)" in registry
    assert str(TRACK29).replace("\\", "/") in registry
    assert metadata["track_id"] == "track29_ontology_mapping_kg_20260625"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    assert "| 8 | Document mapping methodology" in plan
    assert "[x]" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK29.joinpath(required_file).is_file()


def test_track29_checked_in_artifacts_are_present_and_linked() -> None:
    evidence = TRACK29.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("data/ontologies/ontology_mappings.json"),
        Path("data/ontologies/ontology_mappings.schema.json"),
        Path("data/ontologies/ontology_mappings.ttl"),
        Path("data/ontologies/ontology_mappings.jsonld"),
        Path("data/ontologies/ontology_mapping_summary.json"),
        Path("data/ontologies/ontology_mapping_graph.mmd"),
        Path("docs/ontology_mapping.md"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    manifest = json.loads(required_artifacts[0].read_text(encoding="utf-8"))
    summary = json.loads(required_artifacts[4].read_text(encoding="utf-8"))
    mermaid = required_artifacts[5].read_text(encoding="utf-8")

    assert len(manifest["mappings"]) >= 10
    assert summary["mapping_count"] == len(manifest["mappings"])
    assert mermaid.startswith("graph LR")
