"""Narwhals-based dataframe serialization layer for the NLP pipeline.

Provides zero-copy, dataframe-agnostic serialization of pipeline records
to and from the Parquet format using Narwhals for cross-engine compatibility
(Polars, pandas, PyArrow) and msgspec for lightweight struct definitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import msgspec
import narwhals as nw
import pyarrow.parquet as pq

if TYPE_CHECKING:
    from collections.abc import Sequence

# ---------------------------------------------------------------------------
# Schema & Struct
# ---------------------------------------------------------------------------

SCHEMA_FIELDS: list[str] = [
    "doc_id",
    "corpus_source",
    "raw_text",
    "cleaned_tokens",
    "nz_act_citations",
    "te_reo_terms",
    "embeddings",
]
"""Standardised column names for the pipeline output schema.

Each entry corresponds to a field in :class:`PipelineRecord` and is used
to guarantee column ordering when constructing DataFrames and Parquet files.
"""


class PipelineRecord(msgspec.Struct):
    """A single processed document record flowing through the NLP pipeline.

    Parameters
    ----------
    doc_id : str
        Unique document identifier.
    corpus_source : str
        Source corpus (e.g. ``"legislation"`` or ``"hansard"``).
    raw_text : str
        Original raw text of the document.
    cleaned_tokens : list[str]
        Tokenised and cleaned tokens after preprocessing.
    nz_act_citations : list[str]
        New Zealand Act citations detected in the document.
    te_reo_terms : list[str]
        Te Reo Māori terms identified in the document.
    embeddings : list[float] | None
        Optional dense vector embedding generated downstream.
    """

    doc_id: str
    corpus_source: str
    raw_text: str
    cleaned_tokens: list[str]
    nz_act_citations: list[str]
    te_reo_terms: list[str]
    embeddings: list[float] | None = None


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------


def records_to_dataframe(records: Sequence[PipelineRecord]) -> Any:
    """Convert a sequence of pipeline records to a Narwhals-compatible DataFrame.

    Parameters
    ----------
    records : Sequence[PipelineRecord]
        The pipeline records to convert.

    Returns
    -------
    Any
        A Narwhals DataFrame (backed by the default engine, *e.g.* Polars).

    Raises
    ------
    ValueError
        If *records* is empty.
    """
    if not records:
        msg = "Cannot create a DataFrame from an empty sequence of records."
        raise ValueError(msg)

    data: dict[str, list[Any]] = {field: [] for field in SCHEMA_FIELDS}
    for rec in records:
        data["doc_id"].append(rec.doc_id)
        data["corpus_source"].append(rec.corpus_source)
        data["raw_text"].append(rec.raw_text)
        data["cleaned_tokens"].append(rec.cleaned_tokens)
        data["nz_act_citations"].append(rec.nz_act_citations)
        data["te_reo_terms"].append(rec.te_reo_terms)
        data["embeddings"].append(rec.embeddings)

    return nw.from_dict(data, backend="polars")


def serialize_to_parquet(
    records: Sequence[PipelineRecord],
    path: str | Path,
) -> Path:
    """Serialize pipeline records to a Parquet file on disk.

    The records are first converted to a Narwhals DataFrame, then exported
    to a PyArrow table and written via the PyArrow Parquet writer.

    Parameters
    ----------
    records : Sequence[PipelineRecord]
        The pipeline records to persist.
    path : str | Path
        Destination file path for the Parquet output.

    Returns
    -------
    Path
        The resolved (absolute) path of the written Parquet file.

    Raises
    ------
    ValueError
        If *records* is empty.
    """
    output_path = Path(path).resolve()
    df = records_to_dataframe(records)
    native = nw.to_native(df)
    table = native.to_arrow()
    pq.write_table(table, str(output_path))
    return output_path


def load_from_parquet(path: str | Path) -> list[PipelineRecord]:
    """Load pipeline records from a Parquet file on disk.

    Parameters
    ----------
    path : str | Path
        Path to an existing Parquet file written by :func:`serialize_to_parquet`.

    Returns
    -------
    list[PipelineRecord]
        The deserialised pipeline records.

    Raises
    ------
    FileNotFoundError
        If the file at *path* does not exist.
    """
    src = Path(path).resolve()
    if not src.is_file():
        msg = f"Parquet file not found: {src}"
        raise FileNotFoundError(msg)

    table = pq.read_table(str(src))
    df = nw.from_native(table)

    records: list[PipelineRecord] = []
    for row in df.iter_rows(named=True):
        records.append(
            PipelineRecord(
                doc_id=row["doc_id"],
                corpus_source=row["corpus_source"],
                raw_text=row["raw_text"],
                cleaned_tokens=list(row["cleaned_tokens"]),
                nz_act_citations=list(row["nz_act_citations"]),
                te_reo_terms=list(row["te_reo_terms"]),
                embeddings=(
                    list(row["embeddings"]) if row["embeddings"] is not None else None
                ),
            )
        )

    return records


def deserialize_to_dataframe(path: str | Path) -> Any:
    """Load a Parquet file and return a Narwhals DataFrame.

    This is a convenience wrapper around :func:`load_from_parquet` that
    returns the raw Narwhals DataFrame instead of deserialising into
    :class:`PipelineRecord` objects.

    Parameters
    ----------
    path : str | Path
        Path to an existing Parquet file.

    Returns
    -------
    Any
        A Narwhals DataFrame backed by PyArrow.

    Raises
    ------
    FileNotFoundError
        If the file at *path* does not exist.
    """
    src = Path(path).resolve()
    if not src.is_file():
        msg = f"Parquet file not found: {src}"
        raise FileNotFoundError(msg)

    table = pq.read_table(str(src))
    return nw.from_native(table)
