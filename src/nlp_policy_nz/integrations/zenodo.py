"""Zenodo Sandbox API integration for archival deposits.

Provides functions to create, upload to, and publish deposits in the
Zenodo Sandbox environment (https://sandbox.zenodo.org).
"""

import os
from typing import Any

import requests

# ── Constants ────────────────────────────────────────────────────────────────

ZENODO_SANDBOX_API_URL: str = "https://sandbox.zenodo.org/api"
"""Base URL for the Zenodo Sandbox REST API."""

ZENODO_TOKEN_ENV_VAR: str = "ZENODO_SANDBOX_TOKEN"
"""Environment variable that should hold the Zenodo Sandbox personal access
token."""


# ── Custom Exceptions ────────────────────────────────────────────────────────


class DepositError(Exception):
    """Raised when a Zenodo deposit operation fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialise a DepositError.

        Parameters
        ----------
        message : str
            Human-readable description of the error.
        status_code : int | None
            Optional HTTP status code returned by the Zenodo API.
        """
        self.status_code = status_code
        super().__init__(message)


# ── Token Helpers ────────────────────────────────────────────────────────────


def get_zenodo_token() -> str:
    """Load the Zenodo Sandbox token from the environment.

    Returns
    -------
    str
        The personal access token stored in ``ZENODO_SANDBOX_TOKEN``.

    Raises
    ------
    ValueError
        If the environment variable is not set or is empty.
    """
    token = os.environ.get(ZENODO_TOKEN_ENV_VAR, "")
    if not token:
        msg = (
            f"Zenodo Sandbox token not found. "
            f"Set the {ZENODO_TOKEN_ENV_VAR!r} environment variable."
        )
        raise ValueError(msg)
    return token


def _resolve_token(token: str | None) -> str:
    """Return *token* or fall back to the environment variable.

    Parameters
    ----------
    token : str | None
        Explicit token, or ``None`` to read from the environment.

    Returns
    -------
    str
        The resolved access token.
    """
    if token is not None:
        return token
    return get_zenodo_token()


# ── API Helpers ──────────────────────────────────────────────────────────────


def _headers(token: str) -> dict[str, str]:
    """Build standard authorisation headers for Zenodo API calls."""
    return {"Authorization": f"Bearer {token}"}

# ── Public API Functions ─────────────────────────────────────────────────────


def create_sandbox_deposit(
    title: str,
    description: str,
    creators: list[dict[str, Any]],
    token: str | None = None,
) -> dict[str, Any]:
    """Create a new empty deposit in the Zenodo Sandbox.

    Parameters
    ----------
    title : str
        Title of the deposit.
    description : str
        Description / abstract of the deposit.
    creators : list[dict[str, Any]]
        List of creator dicts. Each dict should contain at least a ``"name"``
        key (e.g. ``{"name": "Doe, John", "affiliation": "University"}``).
    token : str | None
        Personal access token. If ``None``, the token is read from the
        ``ZENODO_SANDBOX_TOKEN`` environment variable.

    Returns
    -------
    dict[str, Any]
        The JSON response body from Zenodo containing deposit metadata
        (including the deposit id, links, etc.).

    Raises
    ------
    DepositError
        If the API call fails or returns a non-success status code.
    """
    access_token = _resolve_token(token)
    url = f"{ZENODO_SANDBOX_API_URL}/deposit/depositions"

    body: dict[str, Any] = {
        "metadata": {
            "title": title,
            "description": description,
            "creators": creators,
            "access_right": "open",
            "license": "MIT",
        }
    }

    resp = requests.post(url, json=body, headers=_headers(access_token))

    if not resp.ok:
        msg = (
            f"Failed to create deposit: {resp.status_code} {resp.reason} "
            f"- {resp.text}"
        )
        raise DepositError(msg, status_code=resp.status_code)

    return resp.json()


def upload_file_to_deposit(
    deposit_id: str,
    file_path: str,
    token: str | None = None,
) -> dict[str, Any]:
    """Upload a file to an existing Zenodo Sandbox deposit.

    Parameters
    ----------
    deposit_id : str
        The Zenodo deposit identifier (string form of the integer id).
    file_path : str
        Path to the local file to upload.
    token : str | None
        Personal access token. If ``None``, the token is read from the
        ``ZENODO_SANDBOX_TOKEN`` environment variable.

    Returns
    -------
    dict[str, Any]
        The JSON response body from Zenodo describing the uploaded file.

    Raises
    ------
    DepositError
        If the deposit id is empty, the file does not exist, or the API call
        fails.
    FileNotFoundError
        If the file at *file_path* does not exist.
    """
    if not deposit_id:
        msg = "deposit_id must be a non-empty string."
        raise DepositError(msg)

    access_token = _resolve_token(token)
    url = f"{ZENODO_SANDBOX_API_URL}/deposit/depositions/{deposit_id}/files"

    path = os.fspath(file_path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    filename = os.path.basename(path)

    with open(path, "rb") as fh:
        files = {"file": (filename, fh)}
        resp = requests.post(url, files=files, headers=_headers(access_token))

    if not resp.ok:
        msg = (
            f"Failed to upload file '{filename}': {resp.status_code} "
            f"{resp.reason} - {resp.text}"
        )
        raise DepositError(msg, status_code=resp.status_code)

    return resp.json()


def publish_deposit(
    deposit_id: str,
    token: str | None = None,
) -> dict[str, Any]:
    """Publish (i.e. make public) an existing deposit in the Zenodo Sandbox.

    Parameters
    ----------
    deposit_id : str
        The Zenodo deposit identifier (string form of the integer id).
    token : str | None
        Personal access token. If ``None``, the token is read from the
        ``ZENODO_SANDBOX_TOKEN`` environment variable.

    Returns
    -------
    dict[str, Any]
        The JSON response body from Zenodo containing the published deposit
        metadata, including the DOI.

    Raises
    ------
    DepositError
        If the deposit id is empty or the API call fails.
    """
    if not deposit_id:
        msg = "deposit_id must be a non-empty string."
        raise DepositError(msg)

    access_token = _resolve_token(token)
    url = f"{ZENODO_SANDBOX_API_URL}/deposit/depositions/{deposit_id}/actions/publish"

    resp = requests.post(url, headers=_headers(access_token))

    if not resp.ok:
        msg = (
            f"Failed to publish deposit '{deposit_id}': {resp.status_code} "
            f"{resp.reason} - {resp.text}"
        )
        raise DepositError(msg, status_code=resp.status_code)

    return resp.json()
