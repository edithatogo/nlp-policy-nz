"""Lightweight RAG retrieval prototype wrapping a VectorBackend.

Designed to be a drop-in for Haystack's retriever pattern.  In full
deployment, this would be replaced by Haystack's native
``InMemoryEmbeddingRetriever``, ``LanceDBDocumentStore``, or similar.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nlp_policy_nz.storage.vectordb import LanceDBAdapter

if TYPE_CHECKING:
    from nlp_policy_nz.storage.interfaces import VectorBackend


class HaystackRAGPipeline:
    """Orchestrate embedding-based retrieval with a Haystack-compatible interface.

    Wraps a :class:`VectorBackend` and exposes ``retrieve`` and ``run``
    methods that mirror the Haystack ``Retriever`` / ``Pipeline`` contract,
    returning results in a standardised dict format.

    Parameters
    ----------
    vector_backend : VectorBackend | None
        A :class:`VectorBackend` instance to use for ANN search.
        Defaults to a :class:`LanceDBAdapter`.

    """

    def __init__(self, vector_backend: VectorBackend | None = None) -> None:
        """Initialize the instance."""
        self._backend = vector_backend or LanceDBAdapter()

    def retrieve(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve the top-k nearest neighbours for *query_vector*.

        Parameters
        ----------
        query_vector : list[float]
            The query embedding vector.
        top_k : int
            Number of neighbours to return.  Defaults to ``5``.

        Returns
        -------
        list[dict[str, Any]]
            A list of result dicts as returned by the underlying
            :meth:`VectorBackend.search`.

        """
        return self._backend.search(query_vector, top_k=top_k)

    def run(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Run retrieval and return results in a Haystack-style pipeline format.

        Parameters
        ----------
        query_vector : list[float]
            The query embedding vector.
        top_k : int
            Number of neighbours to return.  Defaults to ``5``.

        Returns
        -------
        dict[str, Any]
            A dict with keys ``"documents"`` (the retrieved records) and
            ``"top_k"`` (the requested count).

        """
        documents = self.retrieve(query_vector, top_k=top_k)
        return {"documents": documents, "top_k": top_k}
