"""Hugging Face Hub dataset upload integration.

Provides functions to convert pipeline Parquet outputs into Hugging Face
``datasets.Dataset`` objects, create dataset repositories on the Hub,
and push data with auto-generated dataset cards.
"""

from __future__ import annotations

import os
from pathlib import Path

import datasets
import pyarrow.parquet as pq
from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HF_TOKEN_ENV_VAR: str = "HF_TOKEN"  # noqa: S105
"""Environment variable holding the Hugging Face access token."""


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class UploadError(Exception):
    """Raised when a Hugging Face Hub upload operation fails."""


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------


def get_hf_token() -> str:
    """Load the Hugging Face token from the environment.

    Returns
    -------
    str
        The token stored in ``HF_TOKEN``.

    Raises
    ------
    ValueError
        If the environment variable is not set.

    """
    token = os.environ.get(HF_TOKEN_ENV_VAR)
    if not token:
        msg = f"Hugging Face token not found. Set the {HF_TOKEN_ENV_VAR!r} environment variable."
        raise ValueError(msg)
    return token


def _resolve_token(token: str | None) -> str | None:
    """Return *token* or fall back to the environment variable."""
    if token is not None:
        return token
    try:
        return get_hf_token()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Core upload functions
# ---------------------------------------------------------------------------


def parquet_to_dataset(parquet_path: str | Path) -> datasets.Dataset:
    """Load a Parquet file and convert it to a Hugging Face ``datasets.Dataset``.

    Parameters
    ----------
    parquet_path : str | Path
        Path to a Parquet file produced by the pipeline.

    Returns
    -------
    datasets.Dataset
        A Hugging Face Dataset backed by the Parquet data.

    Raises
    ------
    FileNotFoundError
        If the Parquet file does not exist.

    """
    src = Path(parquet_path).resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Parquet file not found: {src}")
    table = pq.read_table(str(src))
    return datasets.Dataset(table)


def create_dataset_repo(
    repo_id: str,
    *,
    private: bool = False,
    token: str | None = None,
    exist_ok: bool = True,
) -> str:
    """Create a dataset repository on the Hugging Face Hub.

    Parameters
    ----------
    repo_id : str
        Dataset repository identifier in ``"user/dataset"`` format.
    private : bool
        If ``True``, create a private repository. Defaults to ``False``.
    token : str | None
        Hugging Face access token. Falls back to ``HF_TOKEN`` env var.
    exist_ok : bool
        If ``True``, do not raise an error if the repo already exists.

    Returns
    -------
    str
        The URL of the created (or existing) repository.

    Raises
    ------
    UploadError
        If repository creation fails.

    """
    resolved_token = _resolve_token(token)
    api = HfApi(token=resolved_token)
    try:
        repo_url = api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=private,
            exist_ok=exist_ok,
        )
    except (HfHubHTTPError, Exception) as exc:
        msg = f"Failed to create dataset repo {repo_id!r}: {exc}"
        raise UploadError(msg) from exc
    return str(repo_url)


def push_dataset_to_hub(
    parquet_path: str | Path,
    repo_id: str,
    *,
    split: str = "train",
    private: bool = False,
    token: str | None = None,
    commit_message: str | None = None,
) -> str:
    """Upload a Parquet file to a Hugging Face dataset repository.

    Converts the Parquet file to a ``datasets.Dataset`` and pushes it to
    the specified Hub repository.  The repository is created automatically
    if it does not exist.

    Parameters
    ----------
    parquet_path : str | Path
        Path to the Parquet file to upload.
    repo_id : str
        Target dataset repository (``"user/dataset"`` format).
    split : str
        Dataset split name. Defaults to ``"train"``.
    private : bool
        If ``True``, create a private repository.
    token : str | None
        Hugging Face access token.
    commit_message : str | None
        Custom commit message.  If ``None``, a default is used.

    Returns
    -------
    str
        The URL of the uploaded dataset on the Hub.

    Raises
    ------
    FileNotFoundError
        If the Parquet file does not exist.
    UploadError
        If the upload fails.

    """
    dataset = parquet_to_dataset(parquet_path)

    resolved_token = _resolve_token(token)

    msg = commit_message or f"Upload {Path(parquet_path).name} as {split} split"

    create_dataset_repo(repo_id, private=private, token=token)

    try:
        dataset.push_to_hub(
            repo_id,
            split=split,
            token=resolved_token,
            commit_message=msg,
        )
    except Exception as exc:
        upload_msg = f"Failed to push dataset to {repo_id!r}: {exc}"
        raise UploadError(upload_msg) from exc

    return f"https://huggingface.co/datasets/{repo_id}"


# ---------------------------------------------------------------------------
# Space deployment
# ---------------------------------------------------------------------------


def deploy_space(
    repo_id: str,
    *,
    spaces_dir: str | Path | None = None,
    token: str | None = None,
    commit_message: str | None = None,
    dry_run: bool = False,
) -> str:
    """Deploy a Gradio Space to the Hugging Face Hub.

    Pushes the contents of the ``spaces/`` directory (app.py,
    requirements.txt, README.md) to a Hugging Face Space repository.

    Parameters
    ----------
    repo_id : str
        Hugging Face Space repository identifier (``"user/space"`` format).
    spaces_dir : str | Path | None
        Path to the directory containing the Space files.  If ``None``,
        the ``spaces/`` directory next to the project root is used.
    token : str | None
        Hugging Face access token. Falls back to ``HF_TOKEN`` env var.
    commit_message : str | None
        Custom commit message.  If ``None``, a default is used.
    dry_run : bool
        If ``True``, validate inputs without uploading.

    Returns
    -------
    str
        The URL of the deployed Space on the Hub.

    Raises
    ------
    FileNotFoundError
        If the spaces directory or required files do not exist.
    UploadError
        If the deployment fails.

    """
    if spaces_dir is None:
        pkg_root = Path(__file__).resolve().parent.parent.parent.parent
        spaces_dir = pkg_root / "spaces"

    spaces_path = Path(spaces_dir).resolve()
    if not spaces_path.is_dir():
        msg = f"Spaces directory not found: {spaces_path}"
        raise FileNotFoundError(msg)

    required_files = ["app.py", "requirements.txt"]
    for fname in required_files:
        if not (spaces_path / fname).is_file():
            msg = f"Required file {fname!r} not found in {spaces_path}"
            raise FileNotFoundError(msg)

    resolved_token = _resolve_token(token)
    if not resolved_token:
        msg = (
            f"Hugging Face token not found. "
            f"Set the {HF_TOKEN_ENV_VAR!r} environment variable or pass token."
        )
        raise ValueError(msg)

    if dry_run:
        return f"https://huggingface.co/spaces/{repo_id} (dry-run)"

    msg = commit_message or f"Deploy Gradio Space to {repo_id}"

    api = HfApi(token=resolved_token)
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
        )
        api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=str(spaces_path),
            commit_message=msg,
        )
    except (HfHubHTTPError, Exception) as exc:
        upload_msg = f"Failed to deploy Space to {repo_id!r}: {exc}"
        raise UploadError(upload_msg) from exc

    return f"https://huggingface.co/spaces/{repo_id}"
