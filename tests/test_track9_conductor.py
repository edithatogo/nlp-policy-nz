"""Track 9 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK9 = Path("conductor/tracks/archive/track9_zenodo_20260609")


def test_track9_conductor_registry_and_metadata_are_complete() -> None:
    """Track 9 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK9.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK9.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK9.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 9: Establish Citable Zenodo Archives & Release Workflows (archived)" in registry
    assert str(TRACK9).replace("\\", "/") in registry
    assert metadata["track_id"] == "track9_zenodo_20260609"
    assert metadata["status"] == "archived"
    assert "Track 9: Establish Citable Zenodo Archives" in plan
    assert "Zenodo" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK9.joinpath(required_file).is_file()


def test_track9_evidence_links_zenodo_release_surfaces() -> None:
    """Track 9 evidence records Zenodo archive, release, CLI, and workflow validation."""
    evidence = TRACK9.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/integrations/zenodo.py"),
        Path("src/nlp_policy_nz/integrations/zenodo_archive.py"),
        Path("src/nlp_policy_nz/integrations/release.py"),
        Path(".github/workflows/release.yml"),
        Path("scripts/release.sh"),
        Path("tests/test_zenodo_archive.py"),
        Path("tests/test_release.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "archive-to-zenodo" in evidence
    assert "release" in evidence
    assert "External gates" in evidence
