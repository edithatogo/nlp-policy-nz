"""Track 24 Conductor and mirroring contract tests."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACK24 = ROOT / "conductor" / "tracks" / "multi_git_archive_mirroring_20260614"


def test_track24_conductor_artifacts_exist() -> None:
    """Track 24 keeps the standard Conductor files needed for review."""
    missing = [
        path.name
        for path in [
            TRACK24 / "index.md",
            TRACK24 / "metadata.json",
            TRACK24 / "plan.md",
            TRACK24 / "spec.md",
            TRACK24 / "evidence.md",
        ]
        if not path.is_file()
    ]

    assert missing == []


def test_track24_evidence_records_secret_boundary_and_targets() -> None:
    """Evidence records the locally testable contract and external boundary."""
    evidence = (TRACK24 / "evidence.md").read_text(encoding="utf-8")

    for expected in [
        "GITLAB_MIRROR_URL",
        "CODEBERG_MIRROR_URL",
        "GIT_MIRROR_SSH_PRIVATE_KEY",
        "GitLab",
        "Codeberg",
        "Hugging Face",
        "Zenodo",
        "OSF",
        "operational verification",
    ]:
        assert expected in evidence


def test_track24_index_links_resolve() -> None:
    """The Conductor index links resolve relative to the track folder."""
    index = (TRACK24 / "index.md").read_text(encoding="utf-8")

    for relative_path in ("./spec.md", "./plan.md", "./metadata.json", "./evidence.md"):
        assert relative_path in index
        assert (TRACK24 / relative_path).is_file()
