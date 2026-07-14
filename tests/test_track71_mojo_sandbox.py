"""Track 71 Mojo sandbox contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from experiments.mojo.sandbox import (
    compute_reference_payload,
    detect_mojo_sandbox_report,
    render_reference_json,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
MOJO_KERNEL = ROOT / "experiments" / "mojo" / "kernel.mojo"
TRACK71 = ROOT / "conductor" / "tracks" / "archive" / "track71_mojo_linux_ci_sandbox_20260702"


def _which_linux(name: str) -> str | None:
    """Return a synthetic Linux toolchain layout for sandbox detection tests."""
    return {"mojo": "/opt/mojo/bin/mojo", "pixi": "/opt/bin/pixi", "uv": None}.get(name)


def _which_windows(name: str) -> str | None:
    """Return a synthetic Windows toolchain layout for sandbox detection tests."""
    return {"mojo": None, "pixi": None, "uv": None}.get(name)


def test_track71_repo_artifacts_exist() -> None:
    """Track 71 should ship the sandbox helper and kernel fixture."""
    expected = [
        MOJO_KERNEL,
        ROOT / "docs" / "mojo_sandbox.md",
        ROOT / "experiments" / "mojo" / "sandbox.py",
        TRACK71 / "index.md",
        TRACK71 / "metadata.json",
        TRACK71 / "plan.md",
        TRACK71 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track71_reference_payload_is_deterministic() -> None:
    """The Python reference payload should be stable and easy to compare."""
    payload = compute_reference_payload()

    assert payload.fixture_name == "rolling-signature"
    assert payload.input_values == (1, 2, 3, 5)
    assert payload.prefix_sums == (1, 3, 6, 11)
    assert payload.weighted_sum == 34
    assert payload.checksum == 49
    assert json.loads(render_reference_json())["weighted_sum"] == 34


def test_track71_linux_with_mojo_reports_pass(monkeypatch) -> None:
    """A Linux runner with Mojo installed should report a runnable sandbox."""
    monkeypatch.setattr("experiments.mojo.sandbox.platform.system", lambda: "Linux")
    monkeypatch.setattr("experiments.mojo.sandbox.shutil.which", _which_linux)

    report = detect_mojo_sandbox_report()

    assert report.status == "passed"
    assert report.skip_reason is None
    assert report.install_strategy == "pixi-temporary-project"
    assert report.mojo_available is True


def test_track71_windows_reports_skip(monkeypatch) -> None:
    """Windows should be reported as skipped rather than treated as a failure."""
    monkeypatch.setattr("experiments.mojo.sandbox.platform.system", lambda: "Windows")
    monkeypatch.setattr("experiments.mojo.sandbox.shutil.which", _which_windows)

    report = detect_mojo_sandbox_report()

    assert report.status == "skipped"
    assert report.skip_reason == "Track 71 is Linux-only."
    assert report.mojo_available is False
    assert report.install_strategy == "none"


def test_track71_ci_workflow_contains_optional_sandbox_job() -> None:
    """The CI workflow should include the Linux-only non-blocking sandbox job."""
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "Track 71 Mojo Linux CI sandbox" in workflow
    assert "continue-on-error: true" in workflow
    assert "pixi add mojo" in workflow
    assert "pixi run mojo kernel.mojo" in workflow
    assert "PYTHONPATH=\"$GITHUB_WORKSPACE\" python - <<'PY'" in workflow


def test_track71_sandbox_documentation_covers_usage_skip_and_removal() -> None:
    """The sandbox doc should spell out usage, skip behavior, and removal criteria."""
    doc = (ROOT / "docs" / "mojo_sandbox.md").read_text(encoding="utf-8")

    assert "pixi run python -m experiments.mojo.sandbox --json" in doc
    assert "Non-Linux runners report the sandbox as skipped." in doc
    assert "Remove or archive the sandbox" in doc
