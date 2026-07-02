"""Tests for the Track 73 Mojo optional acceleration deferral record."""

from __future__ import annotations

from pathlib import Path


def test_track73_records_deferral_after_track72_gate_failure() -> None:
    evidence = Path("conductor/tracks/track73_mojo_optional_acceleration_20260702/evidence.md").read_text(
        encoding="utf-8"
    )

    assert "Track 73 is complete as a deferral." in evidence
    assert "Track 72 did not clear the Mojo promotion threshold" in evidence
    assert "No private Mojo kernel is selected for integration." in evidence
    assert "Python fallback remains the canonical path." in evidence

