"""Regression tests for the documented Python runtime support matrix."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_pixi_default_and_experimental_environments_are_explicit() -> None:
    """The default runtime must remain pinned while newer Python lanes probe."""
    manifest = tomllib.loads((ROOT / "pixi.toml").read_text(encoding="utf-8"))
    assert manifest["dependencies"]["python"] == ">=3.11,<3.15"
    environments = manifest["environments"]
    assert environments["default"] == ["py312", "cpu"]
    assert environments["production"] == ["py312", "cpu"]
    assert environments["py313-experimental"] == ["py313", "cpu"]
    assert environments["py314-experimental"] == ["py314", "cpu"]


def test_spacy_and_torch_are_gated_before_python_314() -> None:
    """The ML wheels must not make Python 3.14 resolution claim production support."""
    manifest = tomllib.loads((ROOT / "pixi.toml").read_text(encoding="utf-8"))
    dependencies = manifest["pypi-dependencies"]
    for name in ("spacy", "torch", "bitsandbytes"):
        assert dependencies[name]["env-markers"] == "python_version < '3.14'"

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_dependencies = project["project"]["dependencies"]
    assert any(
        dependency == "spacy>=3.7.0; python_version < '3.14'"
        for dependency in project_dependencies
    )
    assert any(
        dependency == "torch>=2.2.0; python_version < '3.14'"
        for dependency in project_dependencies
    )
