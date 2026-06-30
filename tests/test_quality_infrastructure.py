"""Track 23 quality infrastructure contract tests."""

from __future__ import annotations

import configparser
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_quality_configuration_files_exist() -> None:
    """Coverage, mutation, and documentation artefacts are present."""
    expected_paths = [
        ROOT / ".coveragerc",
        ROOT / "docs" / "build_backend.md",
        ROOT / "docs" / "pydantic_vs_msgspec.md",
        ROOT / "tests" / ".mutatest.toml",
        ROOT / "scripts" / "profile_with_scalene.py",
        ROOT / "scripts" / "benchmark_pipeline_record_msgspec_pydantic.py",
        ROOT / "tests" / "integration" / "__init__.py",
        ROOT / "tests" / "e2e" / "__init__.py",
    ]

    missing = [path for path in expected_paths if not path.is_file()]

    assert missing == []


def test_pyproject_has_strict_quality_tooling() -> None:
    """pyproject enables the strict Ruff, basedpyright, and coverage surfaces."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    selected_rules = set(pyproject["tool"]["ruff"]["lint"]["select"])
    assert {"ANN", "D", "TCH", "YTT", "RET"} <= selected_rules
    assert pyproject["tool"]["basedpyright"]["typeCheckingMode"] == "strict"
    assert pyproject["tool"]["coverage"]["run"]["branch"] is True


def test_coveragerc_matches_pyproject_coverage_policy() -> None:
    """The standalone coverage config is available for CI and local tools."""
    config = configparser.ConfigParser()
    config.read(ROOT / ".coveragerc", encoding="utf-8")

    assert config.get("run", "branch") == "True"
    assert "src" in config.get("run", "source")
    assert "show_missing" in config["report"]


def test_ci_quality_steps_are_wired() -> None:
    """CI runs smoke tests, format, type checking, coverage, and Codecov."""
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "Smoke tests" in workflow
    assert "ruff format" in workflow or "pixi run format" in workflow
    assert "basedpyright" in workflow
    assert "pytest-cov" in workflow or "--cov=src" in workflow
    assert "codecov/codecov-action" in workflow
    assert "workflow_dispatch" in workflow
    assert "Optional mutation tests" in workflow


def test_pixi_quality_tasks_exist() -> None:
    """Pixi exposes the quality commands used by CI and developers."""
    pixi = tomllib.loads((ROOT / "pixi.toml").read_text(encoding="utf-8"))
    tasks = pixi["tasks"]
    dependencies = pixi["pypi-dependencies"]

    for task in ["lint", "format", "coverage", "mutation", "profile", "typecheck"]:
        assert task in tasks
    for dependency in ["scalene", "pytest-cov", "basedpyright", "mutatest"]:
        assert dependency in dependencies
