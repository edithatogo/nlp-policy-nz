"""
Storage Module.

Provides vector storage, document indexing, and retrieval backends using LanceDB,
FAISS, and Polars for efficient storage and querying of processed NLP data.
"""

from __future__ import annotations

from nlp_policy_nz.storage.faiss_adapter import FAISSAdapter
from nlp_policy_nz.storage.haystack_pipeline import HaystackRAGPipeline
from nlp_policy_nz.storage.interfaces import VectorBackend
from nlp_policy_nz.storage.qdrant_adapter import QdrantAdapter
from nlp_policy_nz.storage.serialization import (
    SCHEMA_FIELDS,
    PipelineRecord,
    load_from_parquet,
    records_to_dataframe,
    serialize_to_parquet,
)
from nlp_policy_nz.storage.vectordb import LANCE_DB_URI, LanceDBAdapter

__all__: list[str] = [
    "LANCE_DB_URI",
    "SCHEMA_FIELDS",
    "FAISSAdapter",
    "HaystackRAGPipeline",
    "LanceDBAdapter",
    "PipelineRecord",
    "QdrantAdapter",
    "VectorBackend",
    "load_from_parquet",
    "records_to_dataframe",
    "serialize_to_parquet",
]
