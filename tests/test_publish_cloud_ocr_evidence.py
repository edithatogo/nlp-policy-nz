from __future__ import annotations

from pathlib import Path

import pytest

from scripts.publish_cloud_ocr_evidence import publish_evidence


class FakeApi:
    def __init__(self) -> None:
        self.created: list[tuple[str, str, bool]] = []
        self.uploaded: list[tuple[str, str, str, str, str]] = []

    def create_repo(self, *, repo_id: str, repo_type: str, exist_ok: bool) -> None:
        self.created.append((repo_id, repo_type, exist_ok))

    def upload_folder(
        self,
        *,
        repo_id: str,
        repo_type: str,
        folder_path: str,
        path_in_repo: str,
        commit_message: str,
    ) -> None:
        self.uploaded.append(
            (repo_id, repo_type, folder_path, path_in_repo, commit_message)
        )


def _write_evidence(folder: Path) -> None:
    folder.mkdir()
    for name in ("pilot-gate.json", "reconciled.json", "run-report.json"):
        (folder / name).write_text("{}\n", encoding="utf-8")


def test_publish_evidence_uploads_only_expected_metadata(tmp_path: Path) -> None:
    _write_evidence(tmp_path / "evidence")
    api = FakeApi()

    url = publish_evidence(
        tmp_path / "evidence",
        dataset_id="edithatogo/pilots",
        run_id="pilot-1",
        api=api,
    )

    assert url == "https://huggingface.co/datasets/edithatogo/pilots/tree/main/cloud-ocr-runs/pilot-1"
    assert api.created == [("edithatogo/pilots", "dataset", True)]
    assert api.uploaded[0][3] == "cloud-ocr-runs/pilot-1"


def test_publish_evidence_rejects_unexpected_or_missing_files(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    _write_evidence(evidence)
    (evidence / "ocr.txt").write_text("payload", encoding="utf-8")

    with pytest.raises(ValueError, match="exactly the approved metadata files"):
        publish_evidence(evidence, dataset_id="edithatogo/pilots", run_id="pilot-1", api=FakeApi())

