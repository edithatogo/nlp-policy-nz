"""Track 3 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK3 = Path("conductor/tracks/archive/track3_maori_guard_20260609")


def test_track3_conductor_registry_and_metadata_are_complete() -> None:
    """Track 3 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK3.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK3.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK3.joinpath("spec.md").read_text(encoding="utf-8")

    assert "## [x] Track 3: Implement Māori Language Guard (archived)" in registry
    assert str(TRACK3).replace("\\", "/") in registry
    assert metadata["track_id"] == "track3_maori_guard_20260609"
    assert metadata["status"] == "archived"
    assert "Track 3 Māori Language Guard" in plan
    assert "**Status**: Complete" in spec
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK3.joinpath(required_file).is_file()


def test_track3_evidence_links_guard_surfaces() -> None:
    """Track 3 evidence records the guard modules and validation surface."""
    evidence = TRACK3.joinpath("evidence.md").read_text(encoding="utf-8")
    required_artifacts = (
        Path("src/nlp_policy_nz/guard/normalizer.py"),
        Path("src/nlp_policy_nz/guard/tokenizer_exceptions.py"),
        Path("src/nlp_policy_nz/guard/language_id.py"),
        Path("tests/test_guard.py"),
    )

    for artifact in required_artifacts:
        assert artifact.is_file()
        assert artifact.name in evidence

    assert "Māori" in evidence
    assert "macron" in evidence
    assert "spaCy" in evidence
    assert "External gates" in evidence
