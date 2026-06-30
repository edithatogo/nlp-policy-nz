"""Tests for the Qdrant vector-store adapter (Track 15)."""

from __future__ import annotations

import pytest

pytest.importorskip("qdrant_client")

from nlp_policy_nz.storage.qdrant_adapter import QdrantAdapter  # noqa: E402


def _make_adapter() -> QdrantAdapter:
    return QdrantAdapter(location=":memory:", vector_size=4)


class TestQdrantAdapterInit:
    """Initialisation tests for QdrantAdapter."""

    def test_init_defaults(self) -> None:
        adapter = _make_adapter()
        assert adapter._collection_name == "vectors"
        assert adapter._vector_size == 4


class TestQdrantAdapterCreateAndSearch:
    """Tests for create_index and search."""

    def test_create_and_search(self) -> None:
        adapter = _make_adapter()
        records = [
            {"doc_id": "a", "text": "first", "vector": [1.0, 0.0, 0.0, 0.0]},
            {"doc_id": "b", "text": "second", "vector": [0.0, 1.0, 0.0, 0.0]},
            {"doc_id": "c", "text": "third", "vector": [0.0, 0.0, 1.0, 0.0]},
        ]
        adapter.create_index(records)

        results = adapter.search(query_vector=[1.0, 0.5, 0.0, 0.0], top_k=3)
        assert len(results) == 3
        for r in results:
            assert "score" in r
            assert "doc_id" in r
            assert "text" in r

        adapter.delete_index()

    def test_search_before_create(self) -> None:
        adapter = _make_adapter()
        results = adapter.search(query_vector=[1.0, 0.0, 0.0, 0.0])
        assert results == []


class TestQdrantAdapterAddRecords:
    """Tests for add_records."""

    def test_add_records(self) -> None:
        adapter = _make_adapter()
        adapter.create_index(
            [
                {"doc_id": "a", "text": "first", "vector": [1.0, 0.0, 0.0, 0.0]},
                {"doc_id": "b", "text": "second", "vector": [0.0, 1.0, 0.0, 0.0]},
            ]
        )

        adapter.add_records(
            [
                {"doc_id": "c", "text": "third", "vector": [0.0, 0.0, 1.0, 0.0]},
                {"doc_id": "d", "text": "fourth", "vector": [0.0, 0.0, 0.0, 1.0]},
            ]
        )

        results = adapter.search(query_vector=[1.0, 0.0, 0.0, 0.0], top_k=4)
        assert len(results) == 4
        adapter.delete_index()


class TestQdrantAdapterDelete:
    """Tests for delete_index."""

    def test_delete_index(self) -> None:
        adapter = _make_adapter()
        adapter.create_index(
            [
                {"doc_id": "a", "text": "x", "vector": [1.0, 0.0, 0.0, 0.0]},
            ]
        )
        assert adapter.index_exists() is True

        adapter.delete_index()
        results = adapter.search(query_vector=[1.0, 0.0, 0.0, 0.0])
        assert results == []

    def test_index_exists(self) -> None:
        adapter = _make_adapter()
        assert adapter.index_exists() is False

        adapter.create_index(
            [
                {"doc_id": "a", "text": "x", "vector": [1.0, 0.0, 0.0, 0.0]},
            ]
        )
        assert adapter.index_exists() is True

        adapter.delete_index()
        assert adapter.index_exists() is False
