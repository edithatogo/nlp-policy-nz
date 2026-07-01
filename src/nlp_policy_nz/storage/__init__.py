"""
Storage Module.

Provides vector storage, document indexing, and retrieval backends using LanceDB
and Polars for efficient storage and querying of processed NLP data.

LanceDB is the default supported vector backend. Optional FAISS and Qdrant
adapters remain available from their concrete modules when the matching extras
are installed, but they are intentionally not imported here so the default
package import stays free of optional backend requirements.
"""

from __future__ import annotations

from nlp_policy_nz.storage.haystack_pipeline import HaystackRAGPipeline
from nlp_policy_nz.storage.interfaces import VectorBackend
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
    "HaystackRAGPipeline",
    "LanceDBAdapter",
    "PipelineRecord",
    "VectorBackend",
    "load_from_parquet",
    "records_to_dataframe",
    "serialize_to_parquet",
]
