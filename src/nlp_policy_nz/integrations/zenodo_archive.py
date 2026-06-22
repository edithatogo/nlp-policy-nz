"""High-level Zenodo archive builder.

Provides :class:`ZenodoArchiver` and the convenience function
:func:`archive_to_zenodo` for creating, uploading, and publishing
deposits on the Zenodo Sandbox in a single call.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests

from nlp_policy_nz.integrations.zenodo import (
    DepositError,
    create_sandbox_deposit,
    get_zenodo_token,
    publish_deposit,
    upload_file_to_deposit,
)

logger = logging.getLogger(__name__)


class ZenodoArchiver:
    """High-level interface for creating and publishing Zenodo deposits.

    Wraps the low-level :mod:`nlp_policy_nz.integrations.zenodo` helpers
    into a single class that handles the full create, upload, and publish
    workflow.

    Parameters
    ----------
    token : str | None
        Zenodo personal access token.  If *None* the token is resolved
        from the ``ZENODO_SANDBOX_TOKEN`` environment variable.
    environment : str
        ``"sandbox"`` (default) or ``"production"`` — selects the target
        Zenodo API and the fallback environment variable for the token.

    """

    def __init__(self, token: str | None = None, environment: str = "sandbox") -> None:
        """Initialise the archiver with an optional token override.

        Parameters
        ----------
        token : str | None
            Personal access token.  Falls back to the environment variable
            when *None*.
        environment : str
            ``"sandbox"`` (default) or ``"production"`` — selects the target
            Zenodo API and the fallback environment variable for the token.

        """
        self._token = token
        self._environment = environment

    def _resolve_token(self) -> str:
        """Resolve the access token.

        Returns
        -------
        str
            The resolved personal access token.

        """
        if self._token is not None:
            return self._token
        return get_zenodo_token(environment=self._environment)

    def create_archive(
        self,
        *,
        title: str,
        description: str,
        creators: list[dict[str, Any]],
        file_path: str | Path,
        license_id: str = "MIT",
        provenance_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create, upload, and publish a Zenodo deposit in one step.

        Parameters
        ----------
        title : str
            Title for the Zenodo deposit.
        description : str
            Description / abstract for the deposit.
        creators : list[dict[str, Any]]
            List of creator dicts (each must contain a ``"name"`` key).
        file_path : str | Path
            Path to the local file to upload.
        license_id : str
            SPDX license identifier (default ``"MIT"``).
        provenance_metadata : dict[str, Any] | None
            Optional PROV-O JSON-LD payload to include in deposit metadata.

        Returns
        -------
        dict[str, Any]
            The Zenodo API response for the published deposit.

        Raises
        ------
        FileNotFoundError
            If *file_path* does not exist.
        DepositError
            If any step of the Zenodo API workflow fails.

        """
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        token = self._resolve_token()
        env = self._environment

        logger.info("Creating Zenodo deposit: %s", title)
        deposit = create_sandbox_deposit(
            title=title,
            description=description,
            creators=creators,
            token=token,
            environment=env,
            license_id=license_id,
            provenance_metadata=provenance_metadata,
        )
        deposit_id = str(deposit["id"])

        logger.info("Uploading file to deposit %s ...", deposit_id)
        upload_file_to_deposit(
            deposit_id=deposit_id,
            file_path=str(file_path),
            token=token,
            environment=env,
        )

        logger.info("Publishing deposit %s ...", deposit_id)
        published = publish_deposit(
            deposit_id=deposit_id,
            token=token,
            environment=env,
        )

        logger.info("Deposit published - DOI: %s", published.get("doi", "N/A"))
        return published

    def get_doi(self, deposit_id: str) -> str | None:
        """Retrieve the DOI for a published deposit.

        Parameters
        ----------
        deposit_id : str
            The Zenodo deposit identifier.

        Returns
        -------
        str | None
            The DOI string, or *None* if not yet published.

        Raises
        ------
        DepositError
            If the API request fails.

        """
        from nlp_policy_nz.integrations.zenodo import (
            _get_api_url,
            _headers,
        )  # noqa: PLC0415

        token = self._resolve_token()
        api_url = _get_api_url(self._environment)
        url = f"{api_url}/deposit/depositions/{deposit_id}"
        resp = requests.get(url, headers=_headers(token), timeout=30)

        if not resp.ok:
            msg = (
                f"Failed to fetch deposit '{deposit_id}': "
                f"{resp.status_code} {resp.reason} - {resp.text}"
            )
            raise DepositError(msg, status_code=resp.status_code)

        data: dict[str, Any] = resp.json()
        return data.get("doi")


def archive_to_zenodo(
    title: str,
    description: str,
    creators: list[dict[str, Any]],
    file_path: str | Path,
    token: str | None = None,
    license_id: str = "MIT",
    environment: str = "sandbox",
    provenance_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create and publish a Zenodo deposit.

    Parameters
    ----------
    title : str
        Title for the Zenodo deposit.
    description : str
        Description / abstract for the deposit.
    creators : list[dict[str, Any]]
        List of creator dicts (each must contain a ``"name"`` key).
    file_path : str | Path
        Path to the local file to upload.
    token : str | None
        Personal access token.  Falls back to the environment variable.
    license_id : str
        SPDX license identifier (default ``"MIT"``).
    environment : str
        ``"sandbox"`` (default) or ``"production"`` — selects the target
        Zenodo API and the fallback environment variable for the token.
    provenance_metadata : dict[str, Any] | None
        Optional PROV-O JSON-LD payload to include in deposit metadata.

    Returns
    -------
    dict[str, Any]
        The Zenodo API response for the published deposit.

    Raises
    ------
    FileNotFoundError
        If *file_path* does not exist.
    DepositError
        If any step of the Zenodo API workflow fails.

    """
    archiver = ZenodoArchiver(token=token, environment=environment)
    return archiver.create_archive(
        title=title,
        description=description,
        creators=creators,
        file_path=file_path,
        license_id=license_id,
        provenance_metadata=provenance_metadata,
    )
