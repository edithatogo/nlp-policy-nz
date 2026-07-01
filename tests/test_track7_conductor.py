"""Track 7 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK7 = Path("conductor/tracks/archive/track7_downstream_integration_20260609")


def test_track7_conductor_registry_and_metadata_are_complete() -> None:
    """Track 7 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK7.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK7.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK7.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 7: Design Downstream API & Multi-Agent Verification (archived)" in registry
    assert str(TRACK7).replace("\\", "/") in registry
    assert metadata["track_id"] == "track7_downstream_integration_20260609"
    assert metadata["status"] == "archived"
    assert "Track 7 Downstream API & Multi-Agent Verification" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK7.joinpath(required_file).is_file()


def test_track7_evidence_links_downstream_surfaces() -> None:
    """Track 7 evidence records API, CLI, and graph validation surfaces."""
    evidence = TRACK7.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/api/__init__.py"),
        Path("src/nlp_policy_nz/pipeline_api.py"),
        Path("src/nlp_policy_nz/cli/graph.py"),
        Path("tests/test_graph.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "process_legislation" in evidence
    assert "search_similar" in evidence
    assert "PolicyGraph" in evidence
    assert "External gates" in evidence
