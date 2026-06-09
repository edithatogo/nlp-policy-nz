"""
Hugging Face Hub Integration.

Provides dataset loaders for the New Zealand Hansard and legislation corpora
published on the Hugging Face Hub. Requires a valid Hugging Face token with
read access to the target datasets.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any

import datasets

HF_TOKEN_ENV_VAR: str = "HF_TOKEN"
"""Environment variable name used to store the Hugging Face access token."""


class DatasetLoadError(Exception):
    """Raised when a dataset cannot be loaded from the Hugging Face Hub."""


def get_hf_token() -> str:
    """Retrieve the Hugging Face API token from the environment.

    Returns:
        The Hugging Face token stored in the ``HF_TOKEN`` environment variable.

    Raises:
        ValueError: If the ``HF_TOKEN`` environment variable is not set.
    """
    token = os.environ.get(HF_TOKEN_ENV_VAR)
    if not token:
        msg = (
            f"The {HF_TOKEN_ENV_VAR!r} environment variable is not set. "
            "Please set it to a valid Hugging Face access token with read "
            "permissions for the target dataset repository."
        )
        raise ValueError(msg)
    return token


def _resolve_token(token: str | None) -> str | None:
    """Resolve the Hugging Face token, falling back to the environment.

    Args:
        token: An explicit token, or ``None`` to attempt loading from the
            ``HF_TOKEN`` environment variable.

    Returns:
        The resolved token string, or ``None`` if neither an explicit token
        nor the environment variable is set.
    """
    if token is not None:
        return token
    try:
        return get_hf_token()
    except ValueError:
        return None


def _load_dataset(
    path: str,
    split: str = "train",
    streaming: bool = True,
    token: str | None = None,
) -> Iterable[dict[str, Any]]:
    """Load a Hugging Face dataset from the Hub.

    Args:
        path: The Hugging Face dataset identifier (e.g. ``"username/dataset"``).
        split: Dataset split to load (e.g. ``"train"``, ``"test"``).
        streaming: If ``True``, load the dataset in streaming mode (default).
        token: Optional Hugging Face token. Falls back to the ``HF_TOKEN``
            environment variable if not provided.

    Returns:
        An iterable of dictionaries representing dataset rows.

    Raises:
        DatasetLoadError: If the dataset cannot be found, the token lacks
            permissions, or any other loading error occurs.
    """
    resolved_token = _resolve_token(token)
    try:
        dataset = datasets.load_dataset(
            path,
            split=split,
            streaming=streaming,
            token=resolved_token,
        )
    except Exception as exc:
        msg = f"Failed to load dataset {path!r} (split={split!r}, streaming={streaming!r}): {exc}"
        raise DatasetLoadError(msg) from exc
    return dataset


def load_hansard_dataset(
    split: str = "train",
    streaming: bool = True,
    token: str | None = None,
) -> Iterable[dict[str, Any]]:
    """Load the New Zealand Hansard dataset from the Hugging Face Hub.

    The dataset contains parliamentary debate transcripts from the New Zealand
    House of Representatives.

    Args:
        split: Dataset split to load (default ``"train"``).
        streaming: If ``True`` (default), stream the dataset instead of
            downloading it fully.
        token: Optional Hugging Face access token. If omitted, the loader
            attempts to read the ``HF_TOKEN`` environment variable. If that
            is also unset, the dataset is loaded without authentication.

    Returns:
        An iterable of dictionaries, each representing a Hansard record.

    Raises:
        DatasetLoadError: If the dataset cannot be loaded.
    """
    return _load_dataset(
        path="nz-hansard",
        split=split,
        streaming=streaming,
        token=token,
    )


def load_legislation_dataset(
    split: str = "train",
    streaming: bool = True,
    token: str | None = None,
) -> Iterable[dict[str, Any]]:
    """Load the New Zealand Legislation dataset from the Hugging Face Hub.

    The dataset contains bills, acts, and statutory instruments from the New
    Zealand parliamentary legislative process.

    Args:
        split: Dataset split to load (default ``"train"``).
        streaming: If ``True`` (default), stream the dataset instead of
            downloading it fully.
        token: Optional Hugging Face access token. If omitted, the loader
            attempts to read the ``HF_TOKEN`` environment variable. If that
            is also unset, the dataset is loaded without authentication.

    Returns:
        An iterable of dictionaries, each representing a legislation record.

    Raises:
        DatasetLoadError: If the dataset cannot be loaded.
    """
    return _load_dataset(
        path="nz-legislation",
        split=split,
        streaming=streaming,
        token=token,
    )
