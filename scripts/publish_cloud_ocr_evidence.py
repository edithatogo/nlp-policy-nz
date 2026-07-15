"""Publish a metadata-only Cloud OCR pilot evidence folder to Hugging Face."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Protocol

APPROVED_FILES = frozenset({"pilot-gate.json", "reconciled.json", "run-report.json"})


class HubApi(Protocol):
    """Minimal Hugging Face API surface required by the evidence publisher."""

    def create_repo(self, *, repo_id: str, repo_type: str, exist_ok: bool) -> object:
        """Create the target repository when it does not exist."""
        ...

    def upload_folder(
        self,
        *,
        repo_id: str,
        repo_type: str,
        folder_path: str,
        path_in_repo: str,
        commit_message: str,
    ) -> object:
        """Upload the validated evidence folder."""
        ...


def publish_evidence(
    folder: Path,
    *,
    dataset_id: str,
    run_id: str,
    api: HubApi,
) -> str:
    """Validate and publish only the approved metadata evidence files."""
    files = {path.name for path in folder.iterdir() if path.is_file()}
    if files != APPROVED_FILES:
        raise ValueError("evidence folder must contain exactly the approved metadata files")
    if not dataset_id or not run_id or "/" in run_id or run_id in {".", ".."}:
        raise ValueError("dataset_id and safe run_id are required")
    path_in_repo = f"cloud-ocr-runs/{run_id}"
    api.create_repo(repo_id=dataset_id, repo_type="dataset", exist_ok=True)
    api.upload_folder(
        repo_id=dataset_id,
        repo_type="dataset",
        folder_path=str(folder),
        path_in_repo=path_in_repo,
        commit_message=f"Stage zero-cost cloud OCR pilot {run_id}",
    )
    return f"https://huggingface.co/datasets/{dataset_id}/tree/main/{path_in_repo}"


def main() -> int:
    """Run the metadata-only evidence publication command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--folder", type=Path, required=True)
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        parser.error("HF_TOKEN is required")
    from huggingface_hub import HfApi  # noqa: PLC0415

    url = publish_evidence(
        args.folder,
        dataset_id=args.dataset_id,
        run_id=args.run_id,
        api=HfApi(token=token),
    )
    sys.stdout.write(f"{url}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
