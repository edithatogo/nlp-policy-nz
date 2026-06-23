"""LanceDB vector database integration for nlp-policy-nz.

Provides an Arrow-native embedding index using LanceDB for storing and
retrieving document vectors, supporting fast approximate nearest-neighbour
search over NZ legislative and Hansard corpora.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import lancedb
from lancedb.table import Table

from nlp_policy_nz.storage.interfaces import VectorBackend

LANCE_DB_URI: Final[str] = "./lancedb_data"
"""Default local path for the LanceDB database directory."""


class LanceDBAdapter(VectorBackend):
    """A vector index backed by a LanceDB table.

    Wraps a LanceDB ``Table`` to provide a simple interface for creating,
    querying, and managing embedding collections.  Each record stored in
    the index should contain at least a ``vector``, ``doc_id``, and ``text``
    field.

    Parameters
    ----------
    uri : str | None
        Filesystem path or URI to the LanceDB database.
        Defaults to :data:`LANCE_DB_URI` (``"./lancedb_data"``).
    table_name : str
        Name of the table within the database.  Defaults to ``"embeddings"``.

    Examples
    --------
    >>> idx = LanceDBAdapter()
    >>> idx.create_index([
    ...     {"vector": [0.1, 0.2], "doc_id": "doc1", "text": "example"},
    ... ])
    >>> results = idx.search([0.1, 0.2], top_k=5)

    """

    def __init__(
        self,
        uri: str | None = None,
        table_name: str = "embeddings",
    ) -> None:
        self._uri = str(Path(uri or LANCE_DB_URI).resolve())
        self._table_name = table_name
        self._db: lancedb.DBConnection = lancedb.connect(self._uri)
        self._table: Table | None = None
        self._open_or_create_table()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_index(
        self,
        records: list[dict[str, Any]],
        overwrite: bool = False,
    ) -> None:
        """Create (or overwrite) the table with the given records.

        Parameters
        ----------
        records : list[dict[str, Any]]
            A list of dictionaries.  Each dict **must** include at least the
            keys ``vector`` (``list[float]``), ``doc_id`` (``str``), and
            ``text`` (``str``).
        overwrite : bool
            If ``True``, drop any existing table and re-create it with the
            supplied data.  Default is ``False`` (append if table exists).

        Raises
        ------
        ValueError
            If ``records`` is empty.

        """
        if not records:
            raise ValueError("Cannot create an index with an empty record list.")

        mode = "overwrite" if overwrite else "create"
        try:
            self._table = self._db.create_table(
                self._table_name,
                data=records,
                mode=mode,
            )
        except Exception:
            self._table = self._db.open_table(self._table_name)

    def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for the *top_k* nearest neighbours of *query_vector*.

        Parameters
        ----------
        query_vector : list[float]
            The query embedding vector.
        top_k : int
            Number of nearest neighbours to return.  Defaults to ``10``.

        Returns
        -------
        list[dict[str, Any]]
            A list of result dicts.  Each dict contains the original record
            fields plus a ``score`` key (LanceDB ``_distance`` normalised).
            The ``_distance`` key is also preserved for backwards compat.

        """
        if self._table is None:
            return []

        raw = self._table.search(query_vector).limit(top_k).to_list()
        results: list[dict[str, Any]] = []
        for row in raw:
            row["score"] = row.get("_distance", 0.0)
            results.append(row)
        return results

    def add_records(self, records: list[dict[str, Any]]) -> None:
        """Append records to the existing table.

        Parameters
        ----------
        records : list[dict[str, Any]]
            The records to insert.  Each dict should contain at least
            ``vector``, ``doc_id``, and ``text``.

        Raises
        ------
        RuntimeError
            If the table does not exist yet.

        """
        if self._table is None:
            raise RuntimeError("No table available. Call create_index() first.")
        self._table.add(records)

    def delete_index(self) -> None:
        """Drop the table from the database entirely.

        After calling this method, the index is reset and
        :meth:`create_index` must be called again before any further
        operations.
        """
        if self._table is not None:
            self._db.drop_table(self._table_name)
            self._table = None

    def index_exists(self) -> bool:
        """Check whether the table exists in the database.

        Returns
        -------
        bool
            ``True`` if a table with the configured name exists.

        """
        return self._table_name in self._db.list_tables().tables

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Drop the table and release the LanceDB connection."""
        self.delete_index()
        self._db = None  # type: ignore[assignment]

    def _open_or_create_table(self) -> None:
        """Open an existing table or leave ``_table`` as ``None``."""
        if self.index_exists():
            self._table = self._db.open_table(self._table_name)
        else:
            self._table = None
