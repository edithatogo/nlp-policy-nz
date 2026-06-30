"""FAISS vector storage backend implementing VectorBackend interface."""

from __future__ import annotations

from typing import Any

import numpy as np

from nlp_policy_nz.storage.interfaces import VectorBackend

_HAS_FAISS = True
try:
    import faiss
except ImportError:
    _HAS_FAISS = False


def _normalize(vector: list[float]) -> np.ndarray:
    arr = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(arr)
    if norm > 0:
        arr /= norm
    return arr


class FAISSAdapter(VectorBackend):
    """In-memory vector index using FAISS IndexFlatIP with cosine similarity."""

    def __init__(self, dimension: int) -> None:
        """Initialize the instance."""
        if not _HAS_FAISS:
            msg = "FAISS is required. Install it with: pip install faiss-cpu>=1.8.0"
            raise ImportError(msg)
        self._dimension = dimension
        self._index: faiss.IndexFlatIP | None = None
        self._records: list[tuple[str, str]] = []

    def create_index(
        self,
        records: list[dict[str, Any]],
        overwrite: bool = False,
    ) -> None:
        """Build index from records, optionally resetting existing state."""
        if not records:
            raise ValueError("Cannot create an index with an empty record list.")
        if self._index is not None and not overwrite:
            raise ValueError("An index already exists. Use overwrite=True or add_records().")
        self._index = faiss.IndexFlatIP(self._dimension)
        self._records = []
        vectors = []
        for rec in records:
            vectors.append(_normalize(rec["vector"]))
            self._records.append((rec["doc_id"], rec["text"]))
        if vectors:
            self._index.add(np.stack(vectors))

    def search(
        self,
        query_vector: list[float],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Retrieve top-k results closest to query_vector by cosine similarity."""
        if self._index is None:
            return []
        query = _normalize(query_vector).reshape(1, -1)
        scores, indices = self._index.search(query, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0], strict=True):
            if idx == -1:
                break
            doc_id, text = self._records[idx]
            results.append({"doc_id": doc_id, "text": text, "score": float(score)})
        return results

    def add_records(self, records: list[dict[str, Any]]) -> None:
        """Append records to the existing index, creating one if absent."""
        if self._index is None:
            self._index = faiss.IndexFlatIP(self._dimension)
        vectors = []
        for rec in records:
            vectors.append(_normalize(rec["vector"]))
            self._records.append((rec["doc_id"], rec["text"]))
        if vectors:
            self._index.add(np.stack(vectors))

    def delete_index(self) -> None:
        """Reset the index and clear all stored record mappings."""
        self._index = None
        self._records = []

    def index_exists(self) -> bool:
        """Return True if the internal FAISS index has been created."""
        return self._index is not None

    def close(self) -> None:
        """Release in-memory index (no external connections to close)."""
        self.delete_index()
