"""Tests for the FAISS vector-store adapter (Track 15)."""

from __future__ import annotations

import pytest

pytest.importorskip("faiss")

from nlp_policy_nz.storage.faiss_adapter import FAISSAdapter  # noqa: E402


class TestFAISSAdapterInit:
    """Initialisation tests for FAISSAdapter."""

    def test_init_defaults(self) -> None:
        """Adapter created with dimension but no index exists yet."""
        adapter = FAISSAdapter(dimension=4)
        assert adapter.index_exists() is False
        adapter.delete_index()


class TestFAISSAdapterCreateAndSearch:
    """Tests for create_index and search."""

    def test_create_and_search(self) -> None:
        adapter = FAISSAdapter(dimension=4)
        records = [
            {"doc_id": "a", "text": "first", "vector": [1.0, 0.0, 0.0, 0.0]},
            {"doc_id": "b", "text": "second", "vector": [0.0, 1.0, 0.0, 0.0]},
            {"doc_id": "c", "text": "third", "vector": [0.0, 0.0, 1.0, 0.0]},
        ]
        adapter.create_index(records)

        results = adapter.search(query_vector=[1.0, 0.5, 0.0, 0.0], top_k=3)
        assert len(results) == 3

        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

        doc_ids = [r["doc_id"] for r in results]
        assert doc_ids == ["a", "b", "c"]

        adapter.delete_index()

    def test_search_empty_index(self) -> None:
        adapter = FAISSAdapter(dimension=4)
        assert adapter.search(query_vector=[1.0, 0.0, 0.0, 0.0]) == []
        adapter.delete_index()


class TestFAISSAdapterAddRecords:
    """Tests for add_records."""

    def test_add_records(self) -> None:
        adapter = FAISSAdapter(dimension=4)
        records = [
            {"doc_id": "a", "text": "first", "vector": [1.0, 0.0, 0.0, 0.0]},
            {"doc_id": "b", "text": "second", "vector": [0.0, 1.0, 0.0, 0.0]},
        ]
        adapter.create_index(records)

        adapter.add_records([
            {"doc_id": "c", "text": "third", "vector": [0.0, 0.0, 1.0, 0.0]},
        ])

        results = adapter.search(query_vector=[1.0, 0.0, 0.0, 0.0], top_k=3)
        assert len(results) == 3
        adapter.delete_index()


class TestFAISSAdapterDelete:
    """Tests for delete_index."""

    def test_delete_index(self) -> None:
        adapter = FAISSAdapter(dimension=4)
        adapter.create_index([
            {"doc_id": "a", "text": "x", "vector": [1.0, 0.0, 0.0, 0.0]},
        ])
        assert adapter.index_exists() is True

        adapter.delete_index()
        assert adapter.index_exists() is False
        assert adapter.search(query_vector=[1.0, 0.0, 0.0, 0.0]) == []
