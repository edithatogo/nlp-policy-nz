"""Tests for the LanceDB vector database integration (Task 6.2).

Verifies configuration-level behaviour of :class:`LanceDBAdapter`:
default URI, custom parameters, and edge-case handling for empty
record creation.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from nlp_policy_nz.storage.vectordb import LANCE_DB_URI, LanceDBAdapter


@pytest.fixture
def lancedb_adapter(tmp_path: Path) -> Iterator[LanceDBAdapter]:
    """Return an isolated LanceDB adapter for lifecycle tests."""
    adapter = LanceDBAdapter(uri=str(tmp_path / "lancedb"), table_name="vectors")
    yield adapter
    adapter.close()


@pytest.fixture
def vector_records() -> list[dict[str, object]]:
    """Return small deterministic vector records."""
    return [
        {"doc_id": "a", "text": "first", "vector": [1.0, 0.0, 0.0, 0.0]},
        {"doc_id": "b", "text": "second", "vector": [0.0, 1.0, 0.0, 0.0]},
        {"doc_id": "c", "text": "third", "vector": [0.0, 0.0, 1.0, 0.0]},
    ]

# ---------------------------------------------------------------------------
# Initialisation tests
# ---------------------------------------------------------------------------


class TestLanceDBAdapterInit:
    """Test :meth:`LanceDBAdapter.__init__` with default and custom arguments."""

    def test_adapter_init_defaults(self) -> None:
        """Default URI matches the module constant and table name is
        ``"embeddings"``."""
        idx = LanceDBAdapter()
        default_expected = str(Path(LANCE_DB_URI).resolve())
        assert idx._uri == default_expected
        assert idx._table_name == "embeddings"
        idx.close()

    def test_adapter_init_custom(self) -> None:
        """Custom URI and table name are propagated correctly."""
        custom_uri = str(Path("./custom_lancedb_test").resolve())
        idx = LanceDBAdapter(uri=custom_uri, table_name="my_vectors")
        assert idx._uri == custom_uri
        assert idx._table_name == "my_vectors"
        idx.close()
        shutil.rmtree(custom_uri, ignore_errors=True)


# ---------------------------------------------------------------------------
# Creation edge cases
# ---------------------------------------------------------------------------


class TestLanceDBAdapterCreate:
    """Test :meth:`LanceDBAdapter.create_index` boundary conditions."""

    def test_create_index_with_empty_records(self) -> None:
        """Passing an empty list raises ``ValueError``."""
        idx = LanceDBAdapter()
        with pytest.raises(ValueError, match="empty record list"):
            idx.create_index([])
        idx.close()

    def test_create_index_and_search(
        self,
        lancedb_adapter: LanceDBAdapter,
        vector_records: list[dict[str, object]],
    ) -> None:
        """Creating and searching returns top-k records with similarity scores."""
        lancedb_adapter.create_index(vector_records)

        results = lancedb_adapter.search([1.0, 0.5, 0.0, 0.0], top_k=3)

        assert len(results) == 3
        assert [result["doc_id"] for result in results] == ["a", "b", "c"]
        scores = [result["score"] for result in results]
        assert scores == sorted(scores, reverse=True)
        for result in results:
            assert "score" in result
            assert "_distance" in result
            assert "doc_id" in result
            assert "text" in result

    def test_search_before_create(self, lancedb_adapter: LanceDBAdapter) -> None:
        """Searching before table creation returns an empty result list."""
        assert lancedb_adapter.search([1.0, 0.0, 0.0, 0.0]) == []

    def test_add_records(
        self,
        lancedb_adapter: LanceDBAdapter,
        vector_records: list[dict[str, object]],
    ) -> None:
        """Records can be appended to an existing LanceDB table."""
        lancedb_adapter.create_index(vector_records[:2])
        lancedb_adapter.add_records(vector_records[2:])

        results = lancedb_adapter.search([1.0, 0.0, 0.0, 0.0], top_k=3)

        assert {result["doc_id"] for result in results} == {"a", "b", "c"}

    def test_add_records_requires_existing_index(
        self,
        lancedb_adapter: LanceDBAdapter,
        vector_records: list[dict[str, object]],
    ) -> None:
        """Appending before table creation raises a clear error."""
        with pytest.raises(RuntimeError, match="create_index"):
            lancedb_adapter.add_records(vector_records)

    def test_delete_index(
        self,
        lancedb_adapter: LanceDBAdapter,
        vector_records: list[dict[str, object]],
    ) -> None:
        """Deleting the table makes the index disappear and search empty."""
        lancedb_adapter.create_index(vector_records)
        assert lancedb_adapter.index_exists() is True

        lancedb_adapter.delete_index()

        assert lancedb_adapter.index_exists() is False
        assert lancedb_adapter.search([1.0, 0.0, 0.0, 0.0]) == []

    def test_overwrite_replaces_existing_records(
        self,
        lancedb_adapter: LanceDBAdapter,
        vector_records: list[dict[str, object]],
    ) -> None:
        """Overwrite mode replaces the table contents."""
        lancedb_adapter.create_index(vector_records[:2])
        lancedb_adapter.create_index(vector_records[2:], overwrite=True)

        results = lancedb_adapter.search([0.0, 0.0, 1.0, 0.0], top_k=5)

        assert [result["doc_id"] for result in results] == ["c"]

    def test_distance_to_score_preserves_lower_distance_ordering(self) -> None:
        """Distance conversion must not assume nonnegative L2-style distances."""
        assert LanceDBAdapter._distance_to_score(0.0) == -0.0
        assert LanceDBAdapter._distance_to_score(2.5) == -2.5
        assert LanceDBAdapter._distance_to_score(-2.5) == 2.5
