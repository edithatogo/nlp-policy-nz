"""Qdrant vector-database adapter for nlp-policy-nz.

Provides a :class:`VectorBackend` implementation backed by Qdrant,
supporting both in-process (local / in-memory) and remote (gRPC) modes.
"""

from __future__ import annotations

from typing import Any

from nlp_policy_nz.storage.interfaces import VectorBackend

_HAS_QDRANT = True
try:
    from qdrant_client import QdrantClient as _QdrantClient
    from qdrant_client.http.models import Distance, PointStruct, VectorParams
except ImportError:
    _HAS_QDRANT = False


class QdrantAdapter(VectorBackend):
    """VectorBackend implementation backed by Qdrant.

    Wraps ``qdrant_client.QdrantClient`` to provide a simple interface
    for creating, querying, and managing embedding collections.

    Parameters
    ----------
    location : str | None
        ``None`` or ``":memory:"`` for an in-process in-memory store,
        a filesystem path for local persistent mode, or a URL for a
        remote Qdrant server (gRPC).  Defaults to ``None`` (in-memory).
    collection_name : str
        Name of the Qdrant collection.  Defaults to ``"vectors"``.
    vector_size : int
        Dimensionality of the embedding vectors.  Defaults to ``768``.

    """

    def __init__(
        self,
        location: str | None = None,
        collection_name: str = "vectors",
        vector_size: int = 768,
    ) -> None:
        """Initialize the instance."""
        if not _HAS_QDRANT:
            msg = "Qdrant support requires the qdrant-client package"
            raise ImportError(msg)
        self._collection_name = collection_name
        self._vector_size = vector_size
        self._client = _QdrantClient(location=location)
        self._next_id = 0

    def create_index(
        self,
        records: list[dict[str, Any]],
        overwrite: bool = False,
    ) -> None:
        """Create (or recreate) the Qdrant collection and upsert records.

        Parameters
        ----------
        records : list[dict[str, Any]]
            A list of dictionaries.  Each dict **must** include at least the
            keys ``vector`` (``list[float]``), ``doc_id`` (``str``), and
            ``text`` (``str``).
        overwrite : bool
            If ``True``, drop any existing collection before re-creating it.
            Default is ``False``.

        Raises
        ------
        ValueError
            If *records* is empty.
        RuntimeError
            If a collection already exists and *overwrite* is ``False``.

        """
        if not records:
            raise ValueError("Cannot create an index with an empty record list.")

        if self.index_exists():
            if overwrite:
                self.delete_index()
            else:
                msg = (
                    f"Collection {self._collection_name!r} already exists. "
                    "Use overwrite=True or add_records()."
                )
                raise RuntimeError(msg)

        self._next_id = 0
        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
        )

        if records:
            self.add_records(records)

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
            fields (``doc_id``, ``text``, etc.) plus a ``score`` key.

        """
        if not self.index_exists():
            return []

        hits = self._client.search(
            collection_name=self._collection_name,
            query_vector=query_vector,
            limit=top_k,
        )

        results: list[dict[str, Any]] = []
        for hit in hits:
            result: dict[str, Any] = {"score": hit.score}
            result.update(hit.payload or {})
            results.append(result)
        return results

    def add_records(self, records: list[dict[str, Any]]) -> None:
        """Upsert additional points into the existing collection.

        Parameters
        ----------
        records : list[dict[str, Any]]
            The records to insert.  Each dict should contain at least
            ``vector``, ``doc_id``, and ``text``.

        Raises
        ------
        RuntimeError
            If the collection does not exist yet.

        """
        if not self.index_exists():
            raise RuntimeError(
                "No collection exists. Call create_index() first."
            )

        points: list[PointStruct] = []

        for record in records:
            vector = record.get("vector")
            if not vector:
                msg = f"Record {record.get('doc_id', '?')} has no vector."
                raise ValueError(msg)
            payload = {k: v for k, v in record.items() if k != "vector"}
            points.append(
                PointStruct(
                    id=self._next_id,
                    vector=vector,
                    payload=payload,
                ),
            )
            self._next_id += 1

        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
        )

    def delete_index(self) -> None:
        """Drop the Qdrant collection entirely."""
        if self.index_exists():
            self._client.delete_collection(collection_name=self._collection_name)

    def index_exists(self) -> bool:
        """Check whether the collection exists in Qdrant.

        Returns
        -------
        bool
            ``True`` if a collection with the configured name exists.

        """
        collections = self._client.get_collections()
        return any(c.name == self._collection_name for c in collections.collections)

    def close(self) -> None:
        """Close the Qdrant gRPC connection."""
        self._client.close()
