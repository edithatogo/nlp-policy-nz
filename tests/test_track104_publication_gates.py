"""Tests for Track 104 publication-gate honesty."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_publication_gate_matrix_covers_all_registries_and_boundaries():
    text = (ROOT / "docs/publication-gates.md").read_text(encoding="utf-8")

    for registry in ("Hugging Face", "Zenodo", "PyPI", "OSF"):
        assert registry in text
    assert "Sandbox/test gate" in text
    assert "Production gate" in text
    assert "Green repository CI" in text
    assert "must not be described as production" in text
