"""Micro-benchmark harness for vector store index build and search latency."""

from __future__ import annotations

import pytest

pytest.importorskip("pytest_benchmark")

from nlp_policy_nz.storage.vectordb import LanceDBAdapter
from tests.fixtures.vector_benchmark_data import (  # noqa: E402
    BENCHMARK_DIM,
    BENCHMARK_SIZES,
    generate_benchmark_records,
)

_SEARCH_CORPUS_SIZE = 100


@pytest.mark.benchmark
@pytest.mark.parametrize("n", BENCHMARK_SIZES)
def test_lancedb_index_build_time(benchmark, n):
    records = generate_benchmark_records(n)
    adapter = LanceDBAdapter(table_name=f"bench_lance_build_{n}")
    benchmark(adapter.create_index, records, True)
    adapter.delete_index()


@pytest.mark.benchmark
@pytest.mark.parametrize("top_k", [5, 10, 20])
def test_lancedb_search_latency(benchmark, top_k):
    records = generate_benchmark_records(_SEARCH_CORPUS_SIZE)
    adapter = LanceDBAdapter(table_name="bench_lance_search")
    adapter.create_index(records, overwrite=True)
    query_vec = records[0]["vector"]
    benchmark(adapter.search, query_vec, top_k)
    adapter.delete_index()


@pytest.mark.benchmark
@pytest.mark.parametrize("n", BENCHMARK_SIZES)
def test_faiss_index_build_time(benchmark, n):
    pytest.importorskip("faiss")
    from nlp_policy_nz.storage.faiss_adapter import FAISSAdapter

    records = generate_benchmark_records(n)
    adapter = FAISSAdapter(BENCHMARK_DIM)
    benchmark(adapter.create_index, records, True)
    adapter.delete_index()


@pytest.mark.benchmark
@pytest.mark.parametrize("top_k", [5, 10, 20])
def test_faiss_search_latency(benchmark, top_k):
    pytest.importorskip("faiss")
    from nlp_policy_nz.storage.faiss_adapter import FAISSAdapter

    records = generate_benchmark_records(_SEARCH_CORPUS_SIZE)
    adapter = FAISSAdapter(BENCHMARK_DIM)
    adapter.create_index(records, overwrite=True)
    query_vec = records[0]["vector"]
    benchmark(adapter.search, query_vec, top_k)
    adapter.delete_index()
