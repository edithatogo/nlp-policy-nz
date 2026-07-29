"""Track 100 default and optional dependency contracts."""

from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_core_install_excludes_optional_api_space_and_ml_packages() -> None:
    """Heavy integrations must be opt-in extras, not core requirements."""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    core = set(project["dependencies"])
    excluded = ("fastapi", "uvicorn", "gradio", "plotly", "torch", "transformers", "bitsandbytes")
    assert not any(name.startswith(excluded) for name in core)


def test_track100_extras_are_explicit() -> None:
    """Each optional adoption path has a named install extra."""
    extras = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["optional-dependencies"]
    assert {"api", "space", "ml"} <= extras.keys()
    assert any(item.startswith("fastapi") for item in extras["api"])
    assert any(item.startswith("gradio") for item in extras["space"])
    assert any(item.startswith("torch") for item in extras["ml"])
