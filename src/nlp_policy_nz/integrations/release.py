"""Release workflow and versioning for Zenodo archives.

Provides :class:`ReleaseManager` for creating versioned ``.tar.gz``
archives containing Parquet data and metadata, then publishing them
to Zenodo in a single workflow.
"""

from __future__ import annotations

import json
import logging
import tarfile
import tempfile
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from nlp_policy_nz.integrations.zenodo_archive import ZenodoArchiver

logger = logging.getLogger(__name__)


class ReleaseManager:
    """Manages release archives and their publication to Zenodo.

    Combines local archive creation (``.tar.gz`` with metadata) and
    Zenodo publication into a coherent release workflow.

    Parameters
    ----------
    token : str | None
        Zenodo personal access token.  If *None* the token is resolved
        from the ``ZENODO_SANDBOX_TOKEN`` environment variable.

    """

    def __init__(self, token: str | None = None) -> None:
        """Initialise the release manager.

        Parameters
        ----------
        token : str | None
            Personal access token.  Falls back to the environment variable
            when *None*.

        """
        self._token = token
        self._archiver = ZenodoArchiver(token=token)

    def create_release_archive(
        self,
        parquet_path: str | Path,
        *,
        version: str,
        title: str,
        description: str,
        creators: list[dict[str, Any]],
        output_dir: str | Path | None = None,
    ) -> Path:
        """Create a ``.tar.gz`` release archive from a Parquet file.

        The archive contains the Parquet data file and a ``metadata.json``
        with document count, corpus source, version, title, and other
        provenance information.

        Parameters
        ----------
        parquet_path : str | Path
            Path to the input Parquet file.
        version : str
            Semantic version string (e.g. ``"1.0.0"``).
        title : str
            Human-readable title for the release.
        description : str
            Description / abstract for the release.
        creators : list[dict[str, Any]]
            List of creator dicts for metadata.
        output_dir : str | Path | None
            Directory to write the archive to.  If *None* a temporary
            directory is used.

        Returns
        -------
        Path
            Absolute path to the created ``.tar.gz`` archive.

        Raises
        ------
        FileNotFoundError
            If *parquet_path* does not exist.

        """
        parquet_path = Path(parquet_path).resolve()
        if not parquet_path.is_file():
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

        table = pq.read_table(parquet_path)
        doc_count = len(table)

        metadata: dict[str, Any] = {
            "version": version,
            "title": title,
            "description": description,
            "creators": creators,
            "doc_id_count": doc_count,
            "corpus_source": parquet_path.stem,
            "parquet_file": parquet_path.name,
        }

        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix="nlp_release_"))
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        archive_name = f"nlp-policy-nz-{version}.tar.gz"
        archive_path = output_dir / archive_name

        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(parquet_path, arcname=parquet_path.name)

            metadata_tmp = Path(tempfile.mktemp(suffix=".json"))
            try:
                metadata_tmp.write_text(
                    json.dumps(metadata, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                tar.add(metadata_tmp, arcname="metadata.json")
            finally:
                metadata_tmp.unlink(missing_ok=True)

        logger.info("Release archive created: %s", archive_path)
        return archive_path

    def publish_to_zenodo(
        self,
        archive_path: str | Path,
        *,
        title: str,
        description: str,
        creators: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Publish an existing archive to Zenodo.

        Parameters
        ----------
        archive_path : str | Path
            Path to the ``.tar.gz`` archive to publish.
        title : str
            Title for the Zenodo deposit.
        description : str
            Description / abstract for the deposit.
        creators : list[dict[str, Any]]
            List of creator dicts for the deposit metadata.

        Returns
        -------
        dict[str, Any]
            The Zenodo API response for the published deposit.

        Raises
        ------
        FileNotFoundError
            If *archive_path* does not exist.
        DepositError
            If any Zenodo API call fails.

        """
        return self._archiver.create_archive(
            title=title,
            description=description,
            creators=creators,
            file_path=archive_path,
        )

    def full_release(
        self,
        parquet_path: str | Path,
        *,
        version: str,
        title: str,
        description: str,
        creators: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a release archive and publish it to Zenodo in one step.

        Parameters
        ----------
        parquet_path : str | Path
            Path to the input Parquet file.
        version : str
            Semantic version string (e.g. ``"1.0.0"``).
        title : str
            Human-readable title for the release.
        description : str
            Description / abstract for the release.
        creators : list[dict[str, Any]]
            List of creator dicts for metadata.

        Returns
        -------
        dict[str, Any]
            The Zenodo API response for the published deposit.

        Raises
        ------
        FileNotFoundError
            If *parquet_path* does not exist.
        DepositError
            If any Zenodo API call fails.

        """
        archive_path = self.create_release_archive(
            parquet_path,
            version=version,
            title=title,
            description=description,
            creators=creators,
        )

        logger.info("Publishing release archive to Zenodo ...")
        return self.publish_to_zenodo(
            archive_path,
            title=title,
            description=description,
            creators=creators,
        )
