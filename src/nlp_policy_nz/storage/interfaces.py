"""Abstract interfaces for vector-store backends (Track 15)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class VectorBackend(ABC):
    """Abstract vector-store backend.

    LanceDB is the default local/serverless implementation used by runtime,
    API, CLI, and RAG workflows. FAISS and Qdrant adapters are optional modules
    for benchmark or remote-service experiments and must not be required for
    default imports or CI.
    """

    @abstractmethod
    def create_index(
        self,
        records: list[dict[str, Any]],
        overwrite: bool = False,
    ) -> None:
        """Build a new index from the supplied records.

        All results returned by :meth:`search` include at minimum
        ``"doc_id"``, ``"text"``, and ``"score"`` keys.  ``score`` is
        a similarity value where *higher* means *more relevant*.

        Raises ``ValueError`` if *records* is empty.
        """

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Return the top-k nearest-neighbour results for a query vector.

        Returns an empty list when no index has been created.
        Each result dict contains ``"doc_id"``, ``"text"``, and ``"score"``
        at minimum; backend-specific extras may also be present.
        """

    @abstractmethod
    def add_records(self, records: list[dict[str, Any]]) -> None:
        """Append records to an existing index.

        Raises ``RuntimeError`` if no index has been created yet.
        """

    @abstractmethod
    def delete_index(self) -> None:
        """Remove the entire index and free resources.

        Idempotent — safe to call multiple times.
        """

    @abstractmethod
    def index_exists(self) -> bool:
        """Return True if the index has been created and is queryable."""

    @abstractmethod
    def close(self) -> None:
        """Release backend resources (connections, file handles, etc.).

        Idempotent — safe to call multiple times.
        """
