"""
Storage Module.

Provides vector storage, document indexing, and retrieval backends using LanceDB,
FAISS, and Polars for efficient storage and querying of processed NLP data.
"""

from nlp_policy_nz.storage.serialization import (
    SCHEMA_FIELDS,
    PipelineRecord,
    load_from_parquet,
    records_to_dataframe,
    serialize_to_parquet,
)
from nlp_policy_nz.storage.vectordb import LANCE_DB_URI, VectorIndex

__all__: list[str] = [
    "LANCE_DB_URI",
    "SCHEMA_FIELDS",
    "PipelineRecord",
    "VectorIndex",
    "load_from_parquet",
    "records_to_dataframe",
    "serialize_to_parquet",
]
