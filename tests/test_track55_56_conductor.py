from __future__ import annotations

import json
from pathlib import Path

TRACK55 = Path("conductor/tracks/track55_broad_legislation_extraction_framework_20260630")
TRACK56 = Path("conductor/tracks/track56_rust_accelerated_extraction_runtime_20260630")


def test_tracks_55_and_56_are_registered_complete_and_evidenced() -> None:
    registry = Path("conductor/tracks.md").read_text(encoding="utf-8")

    for marker, track in (
        ("## [x] Track 55: Broad Legislation Extraction Framework", TRACK55),
        ("## [x] Track 56: Rust-Accelerated Extraction Runtime", TRACK56),
    ):
        assert marker in registry
        assert str(track).replace("\\", "/") in registry
        for required_file in ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md"):
            assert track.joinpath(required_file).is_file()


def test_track55_metadata_and_plan_mark_extraction_framework_complete() -> None:
    metadata = json.loads(TRACK55.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK55.joinpath("plan.md").read_text(encoding="utf-8")
    evidence = TRACK55.joinpath("evidence.md").read_text(encoding="utf-8")

    assert metadata["track_id"] == "track55_broad_legislation_extraction_framework_20260630"
    assert "**Status**: Complete" in plan
    assert "SQLite Catalog and Stale-Source Audits" in evidence
    assert "export-extractions" in evidence


def test_track56_metadata_and_plan_mark_runtime_decision_complete() -> None:
    metadata = json.loads(TRACK56.joinpath("metadata.json").read_text(encoding="utf-8"))
    plan = TRACK56.joinpath("plan.md").read_text(encoding="utf-8")
    evidence = TRACK56.joinpath("evidence.md").read_text(encoding="utf-8")

    assert metadata["track_id"] == "track56_rust_accelerated_extraction_runtime_20260630"
    assert "**Status**: Complete" in plan
    assert "Rust Deferral and FFI Boundary" in evidence
    assert "34 tests passed and Ruff passed" in evidence
