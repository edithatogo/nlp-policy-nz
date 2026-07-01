from __future__ import annotations

import json
from pathlib import Path

TRACK31 = Path("conductor/tracks/archive/track31_nz_data_driven_ontologies_20260625")


def test_track31_conductor_registry_and_metadata_are_complete() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK31.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK31.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK31.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 31: New Zealand Data-Driven Ontologies (archived)" in registry
    assert str(TRACK31).replace("\\", "/") in registry
    assert metadata["track_id"] == "track31_nz_data_driven_ontologies_20260625"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    assert "| 8 | Document NZ ontology design decisions" in plan
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK31.joinpath(required_file).is_file()


def test_track31_checked_in_artifacts_are_present_and_linked() -> None:
    evidence = TRACK31.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("data/ontologies/nz_ontology_candidates.json"),
        Path("data/ontologies/nz_ontology_candidates.ttl"),
        Path("data/ontologies/nz_ontology_candidates.jsonld"),
        Path("data/ontologies/nz_controlled_vocabularies.json"),
        Path("docs/nz_ontologies.md"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    manifest = json.loads(required_artifacts[0].read_text(encoding="utf-8"))
    vocabularies = json.loads(required_artifacts[3].read_text(encoding="utf-8"))

    assert manifest["track_id"] == "track31_nz_data_driven_ontologies_20260625"
    assert manifest["summary"]["validation_errors"] == []
    assert manifest["summary"]["concept_count"] == len(manifest["concepts"])
    assert vocabularies["scheme_count"] == len(vocabularies["schemes"])
