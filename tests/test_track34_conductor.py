"""Conductor closeout tests for Track 34."""

from __future__ import annotations

import json
from pathlib import Path

TRACK_DIR = Path("conductor/tracks/archive/track34_publication_protocol_20260625")


def test_track34_conductor_artifacts_mark_archived() -> None:
    """Track 34 conductor artifacts should reflect archive status."""
    metadata = json.loads(TRACK_DIR.joinpath("metadata.json").read_text(encoding="utf-8"))
    spec = TRACK_DIR.joinpath("spec.md").read_text(encoding="utf-8")
    plan = TRACK_DIR.joinpath("plan.md").read_text(encoding="utf-8")
    tracks = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in spec
    assert "**Status**: Complete" in plan
    assert "## [x] Track 34: Standards-Based Publication Protocol (archived)" in tracks
    assert str(TRACK_DIR).replace("\\", "/") in tracks
    assert "- [ ]" not in spec


def test_track34_evidence_names_outputs_and_boundaries() -> None:
    """Track 34 evidence should name protocol outputs and overclaim limits."""
    evidence = TRACK_DIR.joinpath("evidence.md").read_text(encoding="utf-8")
    index = TRACK_DIR.joinpath("index.md").read_text(encoding="utf-8")

    assert "docs/publication_protocol.md" in evidence
    assert "track34_protocol_evidence_map.json" in evidence
    assert "fixture-bounded" in evidence
    assert "docs/publication_protocol.md" in index
