"""Tests for the Track 103 profile onboarding documentation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cookbook_documents_profile_pin_route_and_evaluation_boundary():
    text = (ROOT / "docs/jurisdiction_profiles.md").read_text(encoding="utf-8")

    assert "profile_id" in text
    assert "load_profile_adapter" in text
    assert "licensed smoke fixture" in text
    assert "does not establish legal" in text
