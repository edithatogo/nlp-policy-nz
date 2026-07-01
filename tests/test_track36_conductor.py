"""Conductor implementation tests for Track 36."""

from __future__ import annotations

import json
from pathlib import Path

TRACK_DIR = Path("conductor/tracks/track36_huggingface_exploration_site_20260625")


def test_track36_conductor_artifacts_mark_complete() -> None:
    """Track 36 conductor artifacts should reflect implemented status."""
    metadata = json.loads(TRACK_DIR.joinpath("metadata.json").read_text(encoding="utf-8"))
    spec = TRACK_DIR.joinpath("spec.md").read_text(encoding="utf-8")
    plan = TRACK_DIR.joinpath("plan.md").read_text(encoding="utf-8")
    tracks = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["status"] == "complete"
    assert "**Status**: Complete" in spec
    assert "**Status**: Complete" in plan
    assert "## [x] Track 36: Hugging Face Exploration Site" in tracks
    assert "conductor/tracks/track36_huggingface_exploration_site_20260625" in tracks
    assert "- [ ]" not in spec


def test_track36_evidence_records_space_surface_and_boundaries() -> None:
    """Track 36 evidence should record pages, validation, and full-data limits."""
    evidence = TRACK_DIR.joinpath("evidence.md").read_text(encoding="utf-8")
    index = TRACK_DIR.joinpath("index.md").read_text(encoding="utf-8")

    assert "spaces/app.py" in evidence
    assert "corpus statistics" in evidence
    assert "publication protocol" in evidence
    assert "Full-corpus statistics" in evidence
    assert "Track 36 extends the existing Space" in index
