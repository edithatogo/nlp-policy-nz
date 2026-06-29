"""API layer for nlp-policy-nz.

Exports the FastAPI app and lazy wrappers around the public pipeline API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nlp_policy_nz.api.server import app

if TYPE_CHECKING:
    from pathlib import Path


def process_hansard(
    input_path: str | Path,
    output_path: str | Path,
    generate_embeddings: bool = True,
) -> Path:
    """Lazily process Hansard speech documents through the full NLP pipeline."""
    from nlp_policy_nz.pipeline_api import process_hansard as _process_hansard

    return _process_hansard(input_path, output_path, generate_embeddings)


def process_legislation(
    input_path: str | Path,
    output_path: str | Path,
    generate_embeddings: bool = True,
) -> Path:
    """Lazily process legislation documents through the full NLP pipeline."""
    from nlp_policy_nz.pipeline_api import process_legislation as _process_legislation

    return _process_legislation(input_path, output_path, generate_embeddings)


def search_similar(
    query: str,
    db_path: str = "./lancedb_data",
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Lazily search the vector index for documents similar to a query."""
    from nlp_policy_nz.pipeline_api import search_similar as _search_similar

    return _search_similar(query, db_path=db_path, top_k=top_k)


__all__ = [
    "app",
    "process_hansard",
    "process_legislation",
    "search_similar",
]
