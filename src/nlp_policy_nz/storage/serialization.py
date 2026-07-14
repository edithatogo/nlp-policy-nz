"""Narwhals-based dataframe serialization layer for the NLP pipeline.

Provides zero-copy, dataframe-agnostic serialization of pipeline records
to and from the Parquet format using Narwhals for cross-engine compatibility
(Polars, pandas, PyArrow) and msgspec for lightweight struct definitions.
"""

from __future__ import annotations

from collections.abc import Iterable
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
    "schema_version",
    "doc_id",
    "corpus_source",
    "raw_text",
    "cleaned_tokens",
    "nz_act_citations",
    "te_reo_terms",
    "embeddings",
    "deontic_modality",
    "temporal_expressions",
    "resolved_entities",
    "legal_effect",
    "voting_record",
    "amendments",
    "arguments",
    "argument_label_source",
    "stance",
    "stance_label_source",
    # Committee / submissions additive fields
    "submitter_name",
    "committee",
    "bill_reference",
    "linkage_confidence",
    "challenged_regulation",
    "grounds",
    "report_title",
    "findings",
    "recommendations",
]
"""Standardised column names for the pipeline output schema.

Each entry corresponds to a field in :class:`PipelineRecord` and is used
to guarantee column ordering when constructing DataFrames and Parquet files.

Additive committee/submission fields (optional) are included for
select committee reports, parliament submissions, and regulations
review proceedings.
"""


class PipelineRecord(msgspec.Struct):
    """A single processed document record flowing through the NLP pipeline.

    Parameters
    ----------
    doc_id : str
        Unique document identifier.
    corpus_source : str
        Source corpus (e.g. ``"legislation"``, ``"hansard"``, or
        ``"select_committee"``).
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
    deontic_modality : list[dict[str, str | int | None]]
        Deontic modality annotations detected in the text.
    temporal_expressions : list[dict[str, str | int | None]]
        TimeML-style temporal annotations detected in the text.
    resolved_entities : list[dict[str, Any]]
        Named entity resolution annotations with Wikidata QIDs and confidence scores.
    legal_effect : str | None
        LKIF-inspired legal effect category for the record.
    voting_record : dict[str, Any] | None
        Parsed Hansard division record summary, when the record contains a vote.
    amendments : list[dict[str, Any]]
        Parsed legislative amendment records associated with this pipeline record.
    arguments : list[dict[str, Any]]
        Argument component annotations detected in Hansard debate text.
    argument_label_source : str | None
        Provenance marker for argument labels, such as gold or predicted.
    stance : str | None
        Pro/con/neutral policy stance label for Hansard debate text.
    stance_label_source : str | None
        Provenance marker for stance labels, such as gold or predicted.

    ---- Additive committee / submission fields (optional) ----
    submitter_name : str | None
        Name of the submission author or organisation (parliament submissions).
    committee : str | None
        Name of the select/regulations review committee.
    bill_reference : str | None
        Related bill reference for submissions or committee reports.
    linkage_confidence : float | None
        Confidence score for the cross-corpus bill linkage.
    challenged_regulation : str | None
        Regulation being challenged (regulations review proceedings).
    grounds : str | None
        Grounds for challenging a regulation (regulations review proceedings).
    report_title : str | None
        Title of the select committee report.
    findings : list[str] | None
        Findings extracted from the report.
    recommendations : list[str] | None
        Recommendations extracted from the report.

    """

    doc_id: str
    corpus_source: str
    raw_text: str
    cleaned_tokens: list[str]
    nz_act_citations: list[str]
    te_reo_terms: list[str]
    embeddings: list[float] | None = None
    deontic_modality: list[dict[str, str | int | None]] = msgspec.field(default_factory=list)
    temporal_expressions: list[dict[str, str | int | None]] = msgspec.field(default_factory=list)
    resolved_entities: list[dict[str, Any]] = msgspec.field(default_factory=list)
    legal_effect: str | None = None
    voting_record: dict[str, Any] | None = None
    amendments: list[dict[str, Any]] = msgspec.field(default_factory=list)
    arguments: list[dict[str, Any]] = msgspec.field(default_factory=list)
    argument_label_source: str | None = None
    stance: str | None = None
    stance_label_source: str | None = None

    # ---- Additive committee / submission fields (optional) ----
    submitter_name: str | None = None
    committee: str | None = None
    bill_reference: str | None = None
    linkage_confidence: float | None = None
    challenged_regulation: str | None = None
    grounds: str | None = None
    report_title: str | None = None
    findings: list[str] | None = None
    recommendations: list[str] | None = None
    schema_version: str = "1.1"


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------


def records_to_dataframe(records: Sequence[PipelineRecord]) -> object:
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
        data["schema_version"].append(rec.schema_version)
        data["doc_id"].append(rec.doc_id)
        data["corpus_source"].append(rec.corpus_source)
        data["raw_text"].append(rec.raw_text)
        data["cleaned_tokens"].append(rec.cleaned_tokens)
        data["nz_act_citations"].append(rec.nz_act_citations)
        data["te_reo_terms"].append(rec.te_reo_terms)
        data["embeddings"].append(rec.embeddings)
        data["deontic_modality"].append(rec.deontic_modality)
        data["temporal_expressions"].append(rec.temporal_expressions)
        data["resolved_entities"].append(_normalise_resolved_entities(rec.resolved_entities))
        data["legal_effect"].append(rec.legal_effect)
        data["voting_record"].append(rec.voting_record)
        data["amendments"].append(rec.amendments)
        data["arguments"].append(rec.arguments)
        data["argument_label_source"].append(rec.argument_label_source)
        data["stance"].append(rec.stance)
        data["stance_label_source"].append(rec.stance_label_source)
        # Additive committee / submission fields
        data["submitter_name"].append(rec.submitter_name)
        data["committee"].append(rec.committee)
        data["bill_reference"].append(rec.bill_reference)
        data["linkage_confidence"].append(rec.linkage_confidence)
        data["challenged_regulation"].append(rec.challenged_regulation)
        data["grounds"].append(rec.grounds)
        data["report_title"].append(rec.report_title)
        data["findings"].append(rec.findings)
        data["recommendations"].append(rec.recommendations)

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


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    """Return a schema-safe list of dictionaries from a nested row value."""
    if value is None or isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
        return []
    return [dict(item) for item in value]


def _normalise_resolved_entities(value: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return resolved entities with empty nested context collapsed to null."""
    normalised: list[dict[str, Any]] = []
    for item in value:
        record = dict(item)
        context = record.get("context")
        if isinstance(context, dict) and not context:
            record["context"] = None
        normalised.append(record)
    return normalised


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
                schema_version=row.get("schema_version", "1.1"),
                doc_id=row["doc_id"],
                corpus_source=row["corpus_source"],
                raw_text=row["raw_text"],
                cleaned_tokens=list(row["cleaned_tokens"]),
                nz_act_citations=list(row["nz_act_citations"]),
                te_reo_terms=list(row["te_reo_terms"]),
                embeddings=(list(row["embeddings"]) if row["embeddings"] is not None else None),
                deontic_modality=_list_of_dicts(row.get("deontic_modality")),
                temporal_expressions=_list_of_dicts(row.get("temporal_expressions")),
                resolved_entities=_list_of_dicts(row.get("resolved_entities")),
                legal_effect=row.get("legal_effect"),
                voting_record=(
                    dict(row["voting_record"]) if row.get("voting_record") is not None else None
                ),
                amendments=_list_of_dicts(row.get("amendments")),
                arguments=_list_of_dicts(row.get("arguments")),
                argument_label_source=row.get("argument_label_source"),
                stance=row.get("stance"),
                stance_label_source=row.get("stance_label_source"),
                # Additive committee / submission fields
                submitter_name=row.get("submitter_name"),
                committee=row.get("committee"),
                bill_reference=row.get("bill_reference"),
                linkage_confidence=row.get("linkage_confidence"),
                challenged_regulation=row.get("challenged_regulation"),
                grounds=row.get("grounds"),
                report_title=row.get("report_title"),
                findings=list(row["findings"]) if row.get("findings") is not None else None,
                recommendations=list(row["recommendations"])
                if row.get("recommendations") is not None
                else None,
            )
        )

    return records


def deserialize_to_dataframe(path: str | Path) -> object:
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
