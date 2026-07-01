"""Track 6 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK6 = Path("conductor/tracks/archive/track6_storage_search_20260609")


def test_track6_conductor_registry_and_metadata_are_complete() -> None:
    """Track 6 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK6.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK6.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK6.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 6: Standardize Output Schema & LanceDB Vector Engine (archived)" in registry
    assert str(TRACK6).replace("\\", "/") in registry
    assert metadata["track_id"] == "track6_storage_search_20260609"
    assert metadata["status"] == "archived"
    assert "Track 6 Output Schema & LanceDB Vector Engine" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK6.joinpath(required_file).is_file()


def test_track6_evidence_links_storage_surfaces() -> None:
    """Track 6 evidence records the storage modules and validation surface."""
    evidence = TRACK6.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/storage/serialization.py"),
        Path("src/nlp_policy_nz/storage/vectordb.py"),
        Path("tests/test_storage.py"),
        Path("tests/test_vectordb.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "PipelineRecord" in evidence
    assert "Parquet" in evidence
    assert "LanceDB" in evidence
    assert "External gates" in evidence
