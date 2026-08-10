"""Tests for the Track 105 optional-spike boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_decision_record_keeps_spikes_optional_and_non_authoritative():
    text = (ROOT / "docs/sota-spike-decision.md").read_text(encoding="utf-8")

    assert "Optional extras named `structured`" in text
    assert "promotion_allowed=false" in text
    assert "Banned" in text
    assert "default install" in text
