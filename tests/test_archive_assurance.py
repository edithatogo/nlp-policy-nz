"""Focused tests for the runnable archive assurance harness."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.archive_assurance import (
    AssuranceError,
    check_compatibility,
    check_mutation,
    check_performance,
    check_serializer_canaries,
    mixed_bundle,
    run_assurance,
)


def test_mixed_bundle_covers_public_and_restricted_access() -> None:
    bundle = mixed_bundle()

    assert {source.access_class for source in bundle.sources} == {
        "public",
        "restricted",
    }
    assert any(item.text == "RESTRICTED_ARCHIVE_ASSURANCE_CANARY" for item in bundle.spans)


def test_assurance_lanes_pass_without_external_access(tmp_path: Path) -> None:
    bundle = mixed_bundle()

    assert check_serializer_canaries(bundle, tmp_path)
    assert check_compatibility(bundle, tmp_path)
    assert check_performance()["scale_ratio"] < 8


def test_run_assurance_is_json_serializable_and_can_skip_mutation(tmp_path: Path) -> None:
    report = run_assurance(tmp_path, run_mutation=False)

    assert report["mutation"] == {"status": "skipped"}


def test_mutation_lane_fails_closed_on_nonzero_runner(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailedProcess:
        returncode = 1
        stdout = "SURVIVED"
        stderr = ""

    monkeypatch.setattr(
        "scripts.archive_assurance.subprocess.run", lambda *args, **kwargs: FailedProcess()
    )

    with pytest.raises(AssuranceError, match="mutation assurance failed"):
        check_mutation(Path.cwd())


def test_mutation_command_uses_pinned_compatibility_launcher(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []

    class PassedProcess:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, **kwargs):
        captured.extend(command)
        return PassedProcess()

    monkeypatch.setattr("scripts.archive_assurance.subprocess.run", fake_run)
    from scripts.archive_assurance import check_mutation

    check_mutation(Path.cwd())
    assert captured[0].endswith("python.exe")
    assert captured[1].endswith("run_mutatest_compat.py")
