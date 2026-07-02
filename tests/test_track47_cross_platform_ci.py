"""Track 47 cross-platform CI contract tests."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK47 = ROOT / "conductor" / "tracks" / "track47_cross_platform_ci_20260626"


def test_track47_repo_artifacts_exist() -> None:
    """Track 47 should ship matrix CI, binary build, and platform docs."""
    expected = [
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "workflows" / "build-binaries.yml",
        ROOT / "docs" / "install" / "system_requirements.md",
        TRACK47 / "index.md",
        TRACK47 / "metadata.json",
        TRACK47 / "plan.md",
        TRACK47 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track47_registry_and_plan_are_in_sync() -> None:
    """Track 47 should be recorded as complete with matrix and binary scope."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK47 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK47 / "plan.md").read_text(encoding="utf-8")
    spec = (TRACK47 / "spec.md").read_text(encoding="utf-8")

    assert "Track 47: Cross-Platform CI Matrix & Binary Distribution" in registry
    assert "./conductor/tracks/track47_cross_platform_ci_20260626/" in registry
    assert metadata["track_id"] == "track47_cross_platform_ci_20260626"
    assert metadata["status"] == "complete"
    assert "ubuntu-latest" in plan
    assert "windows-latest" in plan
    assert "macos-latest" in plan
    assert "build-binaries.yml" in plan
    assert "binary distribution" in spec.lower()
    assert "python 3.11 and 3.12" in spec.lower()


def test_track47_ci_and_binary_workflows_are_matrixed() -> None:
    """The workflows should describe matrix testing and release binary publishing."""
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    build_workflow = (ROOT / ".github" / "workflows" / "build-binaries.yml").read_text(encoding="utf-8")
    requirements = (ROOT / "docs" / "install" / "system_requirements.md").read_text(encoding="utf-8")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "ubuntu-latest" in ci_workflow
    assert "windows-latest" in ci_workflow
    assert "macos-latest" in ci_workflow
    assert "3.11" in ci_workflow
    assert "3.12" in ci_workflow
    assert "ci-report" in ci_workflow
    assert "actions/upload-artifact@v4" in ci_workflow
    assert "pyinstaller" in build_workflow.lower()
    assert "softprops/action-gh-release" in build_workflow
    assert "Windows VC" in requirements
    assert "macOS 13" in requirements
    assert pyproject["project"]["requires-python"] == ">=3.11"
