"""API layer for nlp-policy-nz.

Exports lazy wrappers around the public pipeline API and the FastAPI app.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

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
    "API_CONTRACT_VERSION",
    "API_VERSIONS",
    "app",
    "AUTH_SCOPE_MAP",
    "ENDPOINT_INVENTORY",
    "api_contract_summary",
    "api_endpoint_inventory",
    "process_hansard",
    "process_legislation",
    "search_similar",
]


def __getattr__(name: str) -> object:
    """Lazily expose the FastAPI app to avoid importing it on CLI-only paths."""
    if name in {
        "app",
        "API_CONTRACT_VERSION",
        "API_VERSIONS",
        "AUTH_SCOPE_MAP",
        "ENDPOINT_INVENTORY",
        "api_contract_summary",
        "api_endpoint_inventory",
    }:
        server = importlib.import_module("nlp_policy_nz.api.server")
        return getattr(server, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
