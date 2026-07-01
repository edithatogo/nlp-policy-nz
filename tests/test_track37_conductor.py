"""Conductor implementation tests for Track 37."""

from __future__ import annotations

import json
from pathlib import Path

TRACK_DIR = Path("conductor/tracks/track37_publication_manuscript_review_20260625")


def test_track37_conductor_artifacts_mark_complete() -> None:
    """Track 37 conductor artifacts should reflect implemented status."""
    metadata = json.loads(TRACK_DIR.joinpath("metadata.json").read_text(encoding="utf-8"))
    spec = TRACK_DIR.joinpath("spec.md").read_text(encoding="utf-8")
    plan = TRACK_DIR.joinpath("plan.md").read_text(encoding="utf-8")
    tracks = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["status"] == "complete"
    assert "**Status**: Complete" in spec
    assert "**Status**: Complete" in plan
    assert "## [x] Track 37: Publication Manuscript and Review Agents" in tracks
    assert "track37_publication_manuscript_review_20260625" in tracks
    assert "- [ ]" not in spec


def test_track37_evidence_records_review_loop_and_blockers() -> None:
    """Track 37 evidence should record outputs, scores, and external gates."""
    evidence = TRACK_DIR.joinpath("evidence.md").read_text(encoding="utf-8")
    index = TRACK_DIR.joinpath("index.md").read_text(encoding="utf-8")

    assert "artifacts/manuscript/manuscript.md" in evidence
    assert "artifacts/manuscript/manuscript_review_log.json" in evidence
    assert "minimum score above 95" in evidence
    assert "live external reviewer agents" in evidence
    assert "src/nlp_policy_nz/publication/manuscript.py" in index
