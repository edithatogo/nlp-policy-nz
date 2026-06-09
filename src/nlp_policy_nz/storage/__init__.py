"""
Storage Module.

Provides vector storage, document indexing, and retrieval backends using LanceDB,
FAISS, and Polars for efficient storage and querying of processed NLP data.
"""

from nlp_policy_nz.storage.vectordb import LANCE_DB_URI, VectorIndex
from nlp_policy_nz.storage.serialization import (
    PipelineRecord,
    SCHEMA_FIELDS,
    load_from_parquet,
    records_to_dataframe,
    serialize_to_parquet,
)



__all__: list[str] = [
    "LANCE_DB_URI",
    "PipelineRecord",
    "SCHEMA_FIELDS",
    "VectorIndex",
    "load_from_parquet",
    "records_to_dataframe",
    "serialize_to_parquet",
]
