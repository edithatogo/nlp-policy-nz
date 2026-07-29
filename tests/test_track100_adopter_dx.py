"""Contracts for the Track 100 fixture-first adopter path."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_first_run_path_is_consistent_across_user_docs() -> None:
    """README, QUICKSTART, and docs-site must advertise the same local path."""
    documents = (
        ROOT / "README.md",
        ROOT / "QUICKSTART.md",
        ROOT / "docs-site" / "src" / "content" / "docs" / "quickstart.md",
    )
    command_parts = (
        "data/samples/sample_legislation.txt",
        "--output",
        "--source legislation",
        "--no-embeddings",
    )

    for document in documents:
        text = document.read_text(encoding="utf-8")
        assert "nlp-policy-nz process" in text or "pixi run nlp-policy-nz process" in text
        assert all(part in text for part in command_parts), document


def test_fixture_first_run_has_no_compose_requirement() -> None:
    """The canonical fixture and CLI are present independently of Compose."""
    assert (ROOT / "data" / "samples" / "sample_legislation.txt").is_file()
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
    first_path = quickstart.split("3. Optional API/Compose workflow:", maxsplit=1)[0]
    assert "docker compose" not in first_path
