"""Contract tests for the Track 104 CI tier split."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_full_matrix_is_not_pull_request_triggered():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "pull_request:" not in workflow
    assert "schedule:" in workflow
    assert "os: [ubuntu-latest, windows-latest, macos-latest]" in workflow


def test_fast_lane_keeps_security_and_secondary_os_smoke():
    workflow = (ROOT / ".github/workflows/ci-fast.yml").read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert "SAST" in workflow
    assert "SBOM" in workflow
    assert "windows-latest, 3.12 smoke" in workflow
