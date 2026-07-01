"""Conductor contract tests for Track 18."""

from __future__ import annotations

import json
from pathlib import Path

TRACK18 = Path("conductor/tracks/archive/track18_voting_amendments_20260613")


def test_track18_conductor_registry_and_metadata_are_complete() -> None:
    """Track 18 remains discoverable as an archived Conductor track."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK18.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK18.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK18.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 18: Voting Record Analysis & Amendment Tracking (archived)" in registry
    assert str(TRACK18).replace("\\", "/") in registry
    assert metadata["track_id"] == "track18_voting_amendments_20260613"
    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK18.joinpath(required_file).is_file()


def test_track18_evidence_links_voting_and_amendment_surfaces() -> None:
    """Track 18 evidence records parser, schema, pipeline, CLI, and tests."""
    evidence = TRACK18.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/parliament/voting.py"),
        Path("src/nlp_policy_nz/parliament/amendments.py"),
        Path("src/nlp_policy_nz/storage/serialization.py"),
        Path("src/nlp_policy_nz/pipeline_api.py"),
        Path("src/nlp_policy_nz/api/server.py"),
        Path("src/nlp_policy_nz/cli/main.py"),
        Path("tests/test_voting.py"),
        Path("tests/test_amendments.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert str(artifact).replace("\\", "/") in evidence

    assert "voting-summary" in evidence
    assert "amendment-history" in evidence
    assert "external evaluation gate" in evidence


def test_track18_archive_index_links_required_review_artifacts() -> None:
    """The archive index exposes every Track 18 review artifact."""
    index = TRACK18.joinpath("index.md").read_text(encoding="utf-8")

    for file_name in ("spec.md", "plan.md", "metadata.json", "evidence.md"):
        assert file_name in index
