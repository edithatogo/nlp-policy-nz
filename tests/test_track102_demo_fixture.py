"""Tests for the licensed, non-held-out Track 102 demo fixture."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_demo_fixture_provenance_declares_license_and_boundary():
    readme = (ROOT / "data/samples/README.md").read_text(encoding="utf-8")

    assert "MIT license" in readme
    assert "not** held-out" in readme
    assert "adoption_readiness.json" in readme


def test_quickstart_labels_fixture_as_non_evaluative():
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")

    assert "not held-out evaluation data" in quickstart
