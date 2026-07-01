"""Tests for default storage package exports."""

from __future__ import annotations

import builtins
import importlib
from types import ModuleType


def test_storage_import_does_not_require_optional_vector_backends() -> None:
    """Importing the storage package should only require default dependencies."""
    from nlp_policy_nz import storage

    assert storage.LanceDBAdapter is not None
    assert storage.VectorBackend is not None
    assert "FAISSAdapter" not in storage.__all__
    assert "QdrantAdapter" not in storage.__all__


def test_storage_import_succeeds_when_optional_backends_are_missing(monkeypatch) -> None:
    """Reloading storage must not import FAISS or Qdrant optional packages."""
    original_import = builtins.__import__

    def guarded_import(
        name: str,
        globals_: dict[str, object] | None = None,
        locals_: dict[str, object] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> ModuleType:
        if name in {"faiss", "qdrant_client"} or name.startswith("qdrant_client."):
            raise ImportError(name)
        return original_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    from nlp_policy_nz import storage

    reloaded = importlib.reload(storage)
    assert reloaded.LanceDBAdapter is not None
    assert reloaded.VectorBackend is not None


def test_optional_adapter_root_imports_are_lazy_compatible() -> None:
    """Root-level optional adapter lookups remain compatible when installed."""
    from nlp_policy_nz.storage import FAISSAdapter, QdrantAdapter

    assert FAISSAdapter.__name__ == "FAISSAdapter"
    assert QdrantAdapter.__name__ == "QdrantAdapter"
