# Plan: Track 6 Output Schema & LanceDB Vector Engine

This track implements standardized Parquet serialization via Narwhals and LanceDB vector database integration for embedding search.

---

### [x] Task 6.1: Build Narwhals Serialization Layer
- **Action**: Code zero-copy dataframe serialization to Parquet using Narwhals.
- **Why**: Enables standardized, memory-efficient data export.
- **Completed**: Created `storage/serialization.py` with `PipelineRecord` (msgspec Struct), `SCHEMA_FIELDS`, `records_to_dataframe()`, `serialize_to_parquet()`, `load_from_parquet()`, and `deserialize_to_dataframe()` using narwhals + PyArrow.

### [x] Task 6.2: Integrate LanceDB Vector Database
- **Action**: Implement local Arrow-native embedding indices using LanceDB.
- **Why**: Enables local semantic similarity search without external databases.
- **Completed**: Created `storage/vectordb.py` with `VectorIndex` class wrapping LanceDB `Table`, supporting `create_index()`, `search()`, `add_records()`, `delete_table()`, and `table_exists()` methods.

---
