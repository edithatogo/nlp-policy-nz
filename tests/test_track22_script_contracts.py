"""Script contract tests for Track 22 Isaacus dry-run wrappers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_script(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        ["bash", str(ROOT / script), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_isaacus_download_wrapper_is_audit_only_by_default() -> None:
    """Default dataset wrapper output is a local manifest, not a download."""
    result = _run_script("scripts/download_isaacus_datasets.sh")

    assert result.returncode == 0
    assert '"open-australian-legal-corpus"' in result.stdout
    assert "audit_mode" in result.stderr
    assert "download" not in result.stderr.lower()


def test_isaacus_evaluation_wrapper_is_audit_only_by_default() -> None:
    """Default evaluation wrapper output is a local report, not a model/API run."""
    result = _run_script("scripts/evaluate_isaacus_models.sh", "--audit")

    assert result.returncode == 0
    assert "repo-side integration scaffold" in result.stdout
    assert "audit_mode" in result.stderr
    assert "API" not in result.stderr


def test_isaacus_wrappers_reject_live_mode_repo_side() -> None:
    """Live Track 22 activity must fail closed until executed externally."""
    for script in (
        "scripts/download_isaacus_datasets.sh",
        "scripts/evaluate_isaacus_models.sh",
    ):
        result = _run_script(script, "--live")

        assert result.returncode == 64
        assert "live mode is not available" in result.stderr
        assert result.stdout == ""
