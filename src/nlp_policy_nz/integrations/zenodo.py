"""Zenodo Sandbox API integration for archival deposits.

Provides functions to create, upload to, and publish deposits in the
Zenodo Sandbox environment (https://sandbox.zenodo.org).
"""

import os
from pathlib import Path
from typing import Any

import requests

# ── Constants ────────────────────────────────────────────────────────────────

ZENODO_SANDBOX_API_URL: str = "https://sandbox.zenodo.org/api"
"""Base URL for the Zenodo Sandbox REST API."""

ZENODO_PRODUCTION_API_URL: str = "https://zenodo.org/api"
"""Base URL for the Zenodo Production REST API."""

ZENODO_TOKEN_ENV_VAR: str = "ZENODO_SANDBOX_TOKEN"
"""Environment variable that should hold the Zenodo Sandbox personal access
token."""

ZENODO_PRODUCTION_TOKEN: str = "ZENODO_PRODUCTION_TOKEN"
"""Environment variable that should hold the Zenodo Production personal access
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


def get_zenodo_token(environment: str = "sandbox") -> str:
    """Load the Zenodo token from the environment.

    Parameters
    ----------
    environment : str
        ``"sandbox"`` (default) to load ``ZENODO_SANDBOX_TOKEN``, or
        ``"production"`` to load ``ZENODO_PRODUCTION_TOKEN``.

    Returns
    -------
    str
        The personal access token.

    Raises
    ------
    ValueError
        If the environment variable is not set or is empty.
    """
    if environment == "production":
        env_var = ZENODO_PRODUCTION_TOKEN
        label = "Production"
    else:
        env_var = ZENODO_TOKEN_ENV_VAR
        label = "Sandbox"

    token = os.environ.get(env_var, "")
    if not token:
        msg = (
            f"Zenodo {label} token not found. "
            f"Set the {env_var!r} environment variable."
        )
        raise ValueError(msg)
    return token


def _resolve_token(token: str | None, environment: str = "sandbox") -> str:
    """Return *token* or fall back to the environment variable.

    Parameters
    ----------
    token : str | None
        Explicit token, or ``None`` to read from the environment.
    environment : str
        ``"sandbox"`` (default) or ``"production"`` — determines which
        environment variable is read when *token* is ``None``.

    Returns
    -------
    str
        The resolved access token.
    """
    if token is not None:
        return token
    return get_zenodo_token(environment=environment)


# ── API Helpers ──────────────────────────────────────────────────────────────


def _headers(token: str) -> dict[str, str]:
    """Build standard authorisation headers for Zenodo API calls."""
    return {"Authorization": f"Bearer {token}"}


def _get_api_url(environment: str = "sandbox") -> str:
    """Return the Zenodo API base URL for the given *environment*.

    Parameters
    ----------
    environment : str
        ``"sandbox"`` (default) or ``"production"``.

    Returns
    -------
    str
        The base API URL.
    """
    if environment == "production":
        return ZENODO_PRODUCTION_API_URL
    return ZENODO_SANDBOX_API_URL


# ── Public API Functions ─────────────────────────────────────────────────────


def create_sandbox_deposit(
    title: str,
    description: str,
    creators: list[dict[str, Any]],
    token: str | None = None,
    environment: str = "sandbox",
) -> dict[str, Any]:
    """Create a new empty deposit in the Zenodo Sandbox (or Production).

    Parameters
    ----------
    title : str
        Title of the deposit.
    description : str
        Description / abstract of the deposit.
    creators : list[dict[str, Any]]
        List of creator dicts. Each dict should contain at least a ``\"name\"``
        key (e.g. ``{"name": "Doe, John", "affiliation": "University"}``).
    token : str | None
        Personal access token. If ``None``, the token is read from the
        ``ZENODO_SANDBOX_TOKEN`` (or ``ZENODO_PRODUCTION_TOKEN``) environment
        variable, depending on *environment*.
    environment : str
        ``"sandbox"`` (default) or ``"production"`` — selects the API URL and
        the fallback environment variable for the token.

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
    access_token = _resolve_token(token, environment=environment)
    api_url = _get_api_url(environment)
    url = f"{api_url}/deposit/depositions"

    body: dict[str, Any] = {
        "metadata": {
            "title": title,
            "description": description,
            "creators": creators,
            "access_right": "open",
            "license": "MIT",
            "upload_type": "dataset",
        }
    }

    resp = requests.post(url, json=body, headers=_headers(access_token))

    if not resp.ok:
        msg = f"Failed to create deposit: {resp.status_code} {resp.reason} - {resp.text}"
        raise DepositError(msg, status_code=resp.status_code)

    return resp.json()


def upload_file_to_deposit(
    deposit_id: str,
    file_path: str,
    token: str | None = None,
    environment: str = "sandbox",
) -> dict[str, Any]:
    """Upload a file to an existing Zenodo deposit.

    Parameters
    ----------
    deposit_id : str
        The Zenodo deposit identifier (string form of the integer id).
    file_path : str
        Path to the local file to upload.
    token : str | None
        Personal access token. If ``None``, the token is read from the
        ``ZENODO_SANDBOX_TOKEN`` (or ``ZENODO_PRODUCTION_TOKEN``) environment
        variable, depending on *environment*.
    environment : str
        ``"sandbox"`` (default) or ``"production"`` — selects the API URL and
        the fallback environment variable for the token.

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

    access_token = _resolve_token(token, environment=environment)
    api_url = _get_api_url(environment)
    url = f"{api_url}/deposit/depositions/{deposit_id}/files"

    file_path_obj = Path(file_path)
    if not file_path_obj.is_file():
        raise FileNotFoundError(f"File not found: {file_path_obj}")

    filename = file_path_obj.name

    with file_path_obj.open("rb") as fh:
        files = {"file": (filename, fh)}
        resp = requests.post(url, files=files, headers=_headers(access_token))

    if not resp.ok:
        msg = f"Failed to upload file '{filename}': {resp.status_code} {resp.reason} - {resp.text}"
        raise DepositError(msg, status_code=resp.status_code)

    return resp.json()


def publish_deposit(
    deposit_id: str,
    token: str | None = None,
    environment: str = "sandbox",
) -> dict[str, Any]:
    """Publish (i.e. make public) an existing deposit in the Zenodo Sandbox
    (or Production).

    Parameters
    ----------
    deposit_id : str
        The Zenodo deposit identifier (string form of the integer id).
    token : str | None
        Personal access token. If ``None``, the token is read from the
        ``ZENODO_SANDBOX_TOKEN`` (or ``ZENODO_PRODUCTION_TOKEN``) environment
        variable, depending on *environment*.
    environment : str
        ``"sandbox"`` (default) or ``"production"`` — selects the API URL and
        the fallback environment variable for the token.

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

    access_token = _resolve_token(token, environment=environment)
    api_url = _get_api_url(environment)
    url = f"{api_url}/deposit/depositions/{deposit_id}/actions/publish"

    resp = requests.post(url, headers=_headers(access_token))

    if not resp.ok:
        msg = (
            f"Failed to publish deposit '{deposit_id}': {resp.status_code} "
            f"{resp.reason} - {resp.text}"
        )
        raise DepositError(msg, status_code=resp.status_code)

    return resp.json()
