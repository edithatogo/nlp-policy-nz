"""Tests for default storage package exports."""

from __future__ import annotations


def test_storage_import_does_not_require_optional_vector_backends() -> None:
    """Importing the storage package should only require default dependencies."""
    from nlp_policy_nz import storage

    assert storage.LanceDBAdapter is not None
    assert storage.VectorBackend is not None
    assert "FAISSAdapter" not in storage.__all__
    assert "QdrantAdapter" not in storage.__all__
