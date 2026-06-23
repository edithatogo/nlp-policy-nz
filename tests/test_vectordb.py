"""Tests for the LanceDB vector database integration (Task 6.2).

Verifies configuration-level behaviour of :class:`LanceDBAdapter`:
default URI, custom parameters, and edge-case handling for empty
record creation.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.storage.vectordb import LANCE_DB_URI, LanceDBAdapter

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
        idx.delete_index()

    def test_adapter_init_custom(self) -> None:
        """Custom URI and table name are propagated correctly."""
        custom_uri = str(Path("./custom_lancedb_test").resolve())
        idx = LanceDBAdapter(uri=custom_uri, table_name="my_vectors")
        assert idx._uri == custom_uri
        assert idx._table_name == "my_vectors"
        idx.delete_index()
        import shutil  # noqa: PLC0415

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
        idx.delete_index()
