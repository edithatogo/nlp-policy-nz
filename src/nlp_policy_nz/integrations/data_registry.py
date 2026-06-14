"""Data sovereignty registry for tracking dataset provenance and archival.

This module provides a lightweight, JSON-backed registry that records
where each dataset originated, under what license it is distributed,
and where (e.g. which Zenodo DOI) it has been archived.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import msgspec

# ── Data Structures ──────────────────────────────────────────────────────────


class DataRecord(msgspec.Struct, frozen=True):
    """Immutable record of a single dataset's provenance and archival state.

    Attributes
    ----------
    dataset_id : str
        Unique identifier for the dataset (e.g. ``"nz-hansard-v1"``).
    source : str
        Origin description or URL of the source data.
    license : str
        SPDX license identifier (e.g. ``"MIT"``, ``"CC-BY-4.0"``).
    version : str
        Version string for this dataset release.
    doi : str | None
        Digital Object Identifier assigned after archival, if any.
    deposit_url : str | None
        URL to the archived deposit page (e.g. Zenodo record page).
    recorded_at : str
        ISO-8601 UTC timestamp of when this record was created.

    """

    dataset_id: str
    source: str
    license: str
    version: str
    doi: str | None = None
    deposit_url: str | None = None
    recorded_at: str = ""


# ── Registry ─────────────────────────────────────────────────────────────────


class DataSovereigntyRegistry:
    """A local JSON-backed registry for data sovereignty records.

    The registry persists a list of :class:`DataRecord` entries to a
    JSON file on disk, enabling simple lookups and audits of which
    datasets have been archived and where.

    Parameters
    ----------
    registry_path : str | None
        Filesystem path to the JSON registry file. If ``None``, defaults to
        ``./data_registry.json`` relative to the current working directory.

    """

    def __init__(self, registry_path: str | None = None) -> None:
        self._path = Path(registry_path) if registry_path else Path("./data_registry.json")
        self._records: list[DataRecord] = []
        self._load()

    # ── Public API ───────────────────────────────────────────────────────────

    def register(
        self,
        dataset_id: str,
        source: str,
        license_id: str,
        version: str,
        doi: str | None = None,
        deposit_url: str | None = None,
    ) -> DataRecord:
        """Register a new data sovereignty record.

        If a record with the same *dataset_id* already exists it will be
        replaced (updated) by this call.

        Parameters
        ----------
        dataset_id : str
            Unique identifier for the dataset.
        source : str
            Origin description or URL of the source data.
        license_id : str
            SPDX license identifier.
        version : str
            Version string for this release.
        doi : str | None
            Optional DOI assigned after archival.
        deposit_url : str | None
            Optional URL to the archived deposit.

        Returns
        -------
        DataRecord
            The newly created (or updated) record.

        """
        recorded_at = datetime.now(UTC).isoformat()

        record = DataRecord(
            dataset_id=dataset_id,
            source=source,
            license=license_id,
            version=version,
            doi=doi,
            deposit_url=deposit_url,
            recorded_at=recorded_at,
        )

        # Replace existing record with same dataset_id, if any.
        self._records = [r for r in self._records if r.dataset_id != dataset_id]
        self._records.append(record)
        self._save()
        return record

    def lookup(self, dataset_id: str) -> DataRecord | None:
        """Look up a data record by its dataset identifier.

        Parameters
        ----------
        dataset_id : str
            The unique dataset identifier to search for.

        Returns
        -------
        DataRecord | None
            The matching record, or ``None`` if no record is found.

        """
        for record in self._records:
            if record.dataset_id == dataset_id:
                return record
        return None

    def list_records(self) -> list[DataRecord]:
        """Return all registered data records.

        Returns
        -------
        list[DataRecord]
            A copy of the internal list of records.

        """
        return list(self._records)

    # ── Persistence ─────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load records from the JSON registry file on disk.

        If the file does not exist or contains invalid JSON, the
        internal records list is left empty.
        """
        if not self._path.is_file():
            self._records = []
            return

        try:
            raw = self._path.read_text(encoding="utf-8")
            data: list[dict[str, Any]] = json.loads(raw)
            self._records = [msgspec.convert(item, DataRecord) for item in data]
        except (json.JSONDecodeError, OSError, TypeError):
            self._records = []

    def _save(self) -> None:
        """Persist the current records to the JSON registry file."""
        raw = msgspec.json.encode(self._records)
        self._path.write_bytes(raw)
