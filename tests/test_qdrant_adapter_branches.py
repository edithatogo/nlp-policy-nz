from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from nlp_policy_nz.storage import qdrant_adapter as module


@dataclass
class _Hit:
    score: float
    payload: dict[str, Any] | None = None


class _Collections:
    def __init__(self, names: list[str]) -> None:
        self.collections = [SimpleNamespace(name=name) for name in names]


class _FakeClient:
    def __init__(self, location: str | None = None) -> None:  # noqa: ARG002
        self.collection_names: list[str] = []
        self.created: list[tuple[str, Any]] = []
        self.deleted: list[str] = []
        self.upserted: list[tuple[str, list[Any]]] = []
        self.searches: list[tuple[str, list[float], int]] = []
        self.closed = False

    def get_collections(self) -> _Collections:
        return _Collections(self.collection_names)

    def create_collection(self, *, collection_name: str, vectors_config: Any) -> None:
        self.collection_names = [collection_name]
        self.created.append((collection_name, vectors_config))

    def delete_collection(self, *, collection_name: str) -> None:
        self.collection_names = [name for name in self.collection_names if name != collection_name]
        self.deleted.append(collection_name)

    def search(self, *, collection_name: str, query_vector: list[float], limit: int) -> list[_Hit]:
        self.searches.append((collection_name, query_vector, limit))
        return [_Hit(score=0.9, payload={"doc_id": "doc-1", "text": "alpha"})]

    def upsert(self, *, collection_name: str, points: list[Any]) -> None:
        self.upserted.append((collection_name, points))

    def close(self) -> None:
        self.closed = True


def _make_adapter(client: _FakeClient | None = None) -> module.QdrantAdapter:
    adapter = module.QdrantAdapter.__new__(module.QdrantAdapter)
    adapter._collection_name = "vectors"
    adapter._vector_size = 4
    adapter._client = client or _FakeClient()
    adapter._next_id = 0
    return adapter


def _patch_qdrant_types(monkeypatch) -> None:
    monkeypatch.setattr(module, "Distance", SimpleNamespace(COSINE="cosine"), raising=False)
    monkeypatch.setattr(
        module,
        "VectorParams",
        lambda *, size, distance: SimpleNamespace(size=size, distance=distance),
        raising=False,
    )
    monkeypatch.setattr(
        module,
        "PointStruct",
        lambda *, id, vector, payload: SimpleNamespace(id=id, vector=vector, payload=payload),
        raising=False,
    )


def test_init_raises_when_qdrant_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(module, "_HAS_QDRANT", False)
    with pytest.raises(ImportError):
        module.QdrantAdapter()


def test_create_index_and_search_branching(monkeypatch) -> None:
    _patch_qdrant_types(monkeypatch)
    adapter = _make_adapter()
    client = adapter._client

    with pytest.raises(ValueError):
        adapter.create_index([])

    client.collection_names = ["vectors"]
    with pytest.raises(RuntimeError):
        adapter.create_index([{"doc_id": "a", "text": "x", "vector": [1.0, 0.0, 0.0, 0.0]}])

    adapter.create_index(
        [
            {"doc_id": "a", "text": "first", "vector": [1.0, 0.0, 0.0, 0.0]},
            {"doc_id": "b", "text": "second", "vector": [0.0, 1.0, 0.0, 0.0]},
        ],
        overwrite=True,
    )
    assert client.deleted == ["vectors"]
    assert client.created and client.upserted
    assert adapter._next_id == 2

    search_results = adapter.search([1.0, 0.0, 0.0, 0.0], top_k=2)
    assert search_results == [{"score": 0.9, "doc_id": "doc-1", "text": "alpha"}]
    assert client.searches[-1] == ("vectors", [1.0, 0.0, 0.0, 0.0], 2)

    adapter._client.collection_names = []
    assert adapter.search([1.0, 0.0, 0.0, 0.0]) == []


def test_add_records_delete_and_close(monkeypatch) -> None:
    _patch_qdrant_types(monkeypatch)
    adapter = _make_adapter()
    client = adapter._client

    with pytest.raises(RuntimeError):
        adapter.add_records([{"doc_id": "a", "text": "x", "vector": [1.0, 0.0, 0.0, 0.0]}])

    client.collection_names = ["vectors"]
    with pytest.raises(ValueError):
        adapter.add_records([{"doc_id": "missing", "text": "x"}])

    adapter.add_records(
        [
            {"doc_id": "a", "text": "x", "vector": [1.0, 0.0, 0.0, 0.0]},
            {"doc_id": "b", "text": "y", "vector": [0.0, 1.0, 0.0, 0.0]},
        ]
    )
    assert len(client.upserted) == 1
    _, points = client.upserted[0]
    assert [point.id for point in points] == [0, 1]
    assert points[0].payload == {"doc_id": "a", "text": "x"}

    adapter.delete_index()
    assert client.deleted == ["vectors"]

    adapter._client.collection_names = []
    adapter.delete_index()
    adapter.close()
    assert client.closed is True
