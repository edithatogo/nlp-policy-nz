from __future__ import annotations

import json
from pathlib import Path

TRACK30 = Path("conductor/tracks/track30_ontology_mapping_inference_20260625")


def test_track30_conductor_registry_and_metadata_are_complete() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK30.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK30.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK30.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 30: Ontology Mapping Inference" in registry
    assert str(TRACK30).replace("\\", "/") in registry
    assert metadata["track_id"] == "track30_ontology_mapping_inference_20260625"
    assert metadata["status"] == "complete"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    assert "| 8 | Write tests for each inference method" in plan
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK30.joinpath(required_file).is_file()


def test_track30_checked_in_artifacts_are_present_and_linked() -> None:
    evidence = TRACK30.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("data/ontologies/inferred_mapping_candidates.json"),
        Path("data/ontologies/inference_prompts/mapping_interpretation_prompt.json"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    manifest = json.loads(required_artifacts[0].read_text(encoding="utf-8"))
    prompt = json.loads(required_artifacts[1].read_text(encoding="utf-8"))

    assert manifest["track_id"] == "track30_ontology_mapping_inference_20260625"
    assert manifest["candidate_count"] == len(manifest["candidates"])
    assert all(candidate["review_status"] == "needs_review" for candidate in manifest["candidates"])
    assert prompt["task"] == "ontology_mapping_interpretation"
