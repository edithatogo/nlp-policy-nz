"""Conductor closeout tests for Track 32."""

from __future__ import annotations

import json
from pathlib import Path

TRACK_DIR = Path("conductor/tracks/archive/track32_corpus_descriptive_statistics_20260625")


def test_track32_conductor_artifacts_mark_complete() -> None:
    """Track 32 conductor artifacts should reflect implemented status."""
    metadata = json.loads(TRACK_DIR.joinpath("metadata.json").read_text(encoding="utf-8"))
    spec = TRACK_DIR.joinpath("spec.md").read_text(encoding="utf-8")
    plan = TRACK_DIR.joinpath("plan.md").read_text(encoding="utf-8")
    tracks = Path("conductor/tracks.md").read_text(encoding="utf-8")

    assert metadata["status"] == "archived"
    assert "**Status**: Complete" in spec
    assert "**Status**: Complete" in plan
    assert "## [x] Track 32: Whole-Corpus Descriptive Statistics (archived)" in tracks
    assert str(TRACK_DIR).replace("\\", "/") in tracks
    assert "- [ ]" not in spec


def test_track32_evidence_names_outputs_and_boundaries() -> None:
    """Track 32 evidence should record generated outputs and full-corpus limits."""
    evidence = TRACK_DIR.joinpath("evidence.md").read_text(encoding="utf-8")
    index = TRACK_DIR.joinpath("index.md").read_text(encoding="utf-8")

    assert "corpus_statistics_manifest.json" in evidence
    assert "fixture-bounded" in evidence
    assert "PipelineRecord Parquet" in evidence
    assert "docs/corpus_statistics.md" in index
