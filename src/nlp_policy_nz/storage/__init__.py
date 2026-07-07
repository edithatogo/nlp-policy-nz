"""
Storage Module.

Provides vector storage, document indexing, and retrieval backends using LanceDB
and Polars for efficient storage and querying of processed NLP data.

LanceDB is the default supported vector backend. Optional adapters remain
available from their concrete modules when the matching extras are installed,
but they are intentionally not imported here so the default package import
stays free of optional backend requirements.
"""

from __future__ import annotations

from nlp_policy_nz.storage.interfaces import VectorBackend
from nlp_policy_nz.storage.serialization import (
    SCHEMA_FIELDS,
    PipelineRecord,
    load_from_parquet,
    records_to_dataframe,
    serialize_to_parquet,
)

__all__: list[str] = [
    "SCHEMA_FIELDS",
    "HaystackRAGPipeline",
    "LanceDBAdapter",
    "PipelineRecord",
    "VectorBackend",
    "load_from_parquet",
    "records_to_dataframe",
    "serialize_to_parquet",
]


def __getattr__(name: str) -> object:
    """Lazily resolve optional vector adapters without hard dependencies."""
    if name == "LANCE_DB_URI":
        from nlp_policy_nz.storage.vectordb import LANCE_DB_URI

        return LANCE_DB_URI
    if name == "HaystackRAGPipeline":
        from nlp_policy_nz.storage.haystack_pipeline import HaystackRAGPipeline

        return HaystackRAGPipeline
    if name == "LanceDBAdapter":
        from nlp_policy_nz.storage.vectordb import LanceDBAdapter

        return LanceDBAdapter
    if name == "FAISSAdapter":
        from nlp_policy_nz.storage.faiss_adapter import FAISSAdapter

        return FAISSAdapter
    if name == "QdrantAdapter":
        from nlp_policy_nz.storage.qdrant_adapter import QdrantAdapter

        return QdrantAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
