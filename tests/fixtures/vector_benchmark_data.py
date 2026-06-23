"""Synthetic vector data generators for Track 15 benchmark harness."""

from __future__ import annotations

import random
from typing import Any

BENCHMARK_DIM: int = 768
BENCHMARK_SIZES: list[int] = [10, 100, 1000]


def generate_benchmark_records(n: int, dim: int = 768) -> list[dict[str, Any]]:
    """Return *n* synthetic records with random vectors of length *dim*.

    Each record contains ``vector`` (``list[float]``), ``doc_id``
    (``"doc_0"`` … ``"doc_n"``), and placeholder ``text``.
    """
    rng = random.Random(42)
    return [
        {
            "vector": [rng.random() for _ in range(dim)],
            "doc_id": f"doc_{i}",
            "text": f"Synthetic document {i} for vector benchmark testing.",
        }
        for i in range(n)
    ]


def generate_queries(n: int, dim: int = 768) -> list[tuple[list[float], str]]:
    """Return *n* query vectors whose nearest neighbour should be ``doc_0``.

    Each element is a ``(query_vector, expected_doc_id)`` pair.
    The query vector is a small perturbation of the first record's vector so
    that the closest match in a cosine-similarity index should be ``doc_0``.
    """
    ref_records = generate_benchmark_records(1, dim)
    doc_0_vec = ref_records[0]["vector"]
    rng = random.Random(7)
    return [
        (
            [v + (rng.random() - 0.5) * 0.01 for v in doc_0_vec],
            "doc_0",
        )
        for _ in range(n)
    ]
