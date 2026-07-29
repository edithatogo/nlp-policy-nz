"""Track 100 Compose and quickstart honesty contracts."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_compose_labels_volume_holder_stubs() -> None:
    """Volume-holder services must not be presented as database servers."""
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "Stub volume-holder" in compose
    assert compose.count("Stub volume-holder") >= 2


def test_quickstarts_place_optional_api_after_fixture_path() -> None:
    """Both quickstarts must identify the API/Compose path as optional."""
    root = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
    site = (ROOT / "docs-site" / "src" / "content" / "docs" / "quickstart.md").read_text(encoding="utf-8")
    assert "Optional API/Compose workflow" in root
    assert "Optional API path" in site
    assert "volume-holder stubs" in root
    assert "volume-holder" in site
