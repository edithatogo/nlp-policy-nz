"""Track 63 Conductor artifact contract tests."""

from __future__ import annotations

import json
from pathlib import Path

TRACK63 = Path("conductor/tracks/track63_nlprule_grammar_matching_eval_20260701")


def test_track63_conductor_registry_and_metadata_are_complete() -> None:
    """Track 63 keeps the standard Conductor files needed for review."""
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")
    metadata = json.loads(TRACK63.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK63.joinpath("plan.md").read_text(encoding="utf-8")
    spec = TRACK63.joinpath("spec.md").read_text(encoding="utf-8")
    index = TRACK63.joinpath("index.md").read_text(encoding="utf-8")
    evidence = TRACK63.joinpath("evidence.md").read_text(encoding="utf-8")

    assert "## [x] Track 63: nlprule Grammar and Rule Matching Evaluation" in registry
    assert str(TRACK63).replace("\\", "/") in registry
    assert metadata["track_id"] == "track63_nlprule_grammar_matching_eval_20260701"
    assert metadata["status"] == "planned"
    assert "Track 63: nlprule Grammar and Rule Matching Evaluation" in plan
    assert "Track 63" in spec
    assert "Track 63" in index
    assert "Track 63" in evidence
    for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
        assert TRACK63.joinpath(required_file).is_file()
