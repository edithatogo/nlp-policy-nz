"""Track 4 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK4 = Path("conductor/tracks/archive/track4_syntactic_layer_20260609")


def test_track4_conductor_registry_and_metadata_are_complete() -> None:
    """Track 4 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK4.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK4.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK4.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 4: Build Versioned Universal Ingestion Engine & Schema Emitters (v1 & v2) (archived)" in registry
    assert str(TRACK4).replace("\\", "/") in registry
    assert metadata["track_id"] == "track4_syntactic_layer_20260609"
    assert metadata["status"] == "archived"
    assert "Track 4 Syntactic Parsing & Citation Extractor" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK4.joinpath(required_file).is_file()


def test_track4_evidence_links_syntactic_surfaces() -> None:
    """Track 4 evidence records the syntactic modules and validation surface."""
    evidence = TRACK4.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/syntactic/pipeline.py"),
        Path("src/nlp_policy_nz/syntactic/citations.py"),
        Path("src/nlp_policy_nz/syntactic/chunking.py"),
        Path("tests/test_syntactic.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "spaCy" in evidence
    assert "Māori Guard" in evidence
    assert "EntityRuler" in evidence
    assert "External gates" in evidence
