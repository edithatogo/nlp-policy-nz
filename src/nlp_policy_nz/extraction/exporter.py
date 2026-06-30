"""Export pipeline records as broad extraction manifests."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from nlp_policy_nz.axiom import pipeline_record_rulespec_reference, source_sha256
from nlp_policy_nz.extraction.schemas import (
    ExtractedSpan,
    ExtractionFamily,
    ExtractionManifest,
    ExtractionRecord,
    SourceTrace,
    extraction_manifest_from_records,
    render_extraction_manifest_json,
)
from nlp_policy_nz.storage import PipelineRecord, load_from_parquet


def extraction_manifest_from_pipeline_records(
    records: Iterable[PipelineRecord],
    *,
    retrieved_at: str,
    source_url_base: str = "pipeline://records",
) -> ExtractionManifest:
    """Build a source-grounded extraction manifest from pipeline records."""
    extraction_records: list[ExtractionRecord] = []
    for record in records:
        source_trace = _source_trace_for_record(
            record,
            retrieved_at=retrieved_at,
            source_url_base=source_url_base,
        )
        extraction_records.extend(_records_for_pipeline_record(record, source_trace))
    return extraction_manifest_from_records(tuple(extraction_records))


def export_extraction_manifest_from_parquet(
    parquet_path: str | Path,
    output_path: str | Path,
    *,
    retrieved_at: str,
    source_url_base: str = "pipeline://records",
) -> Path:
    """Load pipeline Parquet rows and write an extraction manifest JSON file."""
    records = load_from_parquet(parquet_path)
    manifest = extraction_manifest_from_pipeline_records(
        records,
        retrieved_at=retrieved_at,
        source_url_base=source_url_base,
    )
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_extraction_manifest_json(manifest), encoding="utf-8")
    return output


def _records_for_pipeline_record(
    record: PipelineRecord,
    source_trace: SourceTrace,
) -> list[ExtractionRecord]:
    """Return extraction records represented by one pipeline row."""
    exports: list[ExtractionRecord] = []
    exports.extend(_deontic_records(record, source_trace))
    exports.extend(_temporal_records(record, source_trace))
    exports.extend(_entity_records(record, source_trace))
    exports.extend(_amendment_records(record, source_trace))
    exports.extend(_cross_reference_records(record, source_trace))
    if record.legal_effect:
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "legal_effect", 0),
                family=_family_from_legal_effect(record.legal_effect),
                label=str(record.legal_effect),
                value=record.legal_effect,
                source_trace=source_trace,
                attributes={"source_field": "legal_effect"},
            )
        )
    if record.legal_effect or record.deontic_modality:
        reference = pipeline_record_rulespec_reference(record)
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "rules_as_code", 0),
                family=ExtractionFamily.RULES_AS_CODE,
                label="candidate RuleSpec bridge",
                value=reference.durable_id,
                source_trace=source_trace,
                confidence=0.8,
                attributes={
                    "rulespec_id": reference.durable_id,
                    "source_field": "legal_effect"
                    if record.legal_effect
                    else "deontic_modality",
                },
            )
        )
    return exports


def _deontic_records(
    record: PipelineRecord,
    source_trace: SourceTrace,
) -> list[ExtractionRecord]:
    exports: list[ExtractionRecord] = []
    for index, annotation in enumerate(record.deontic_modality):
        label = _annotation_label(annotation, fallback="deontic modality")
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "deontic", index),
                family=_family_from_deontic(label),
                label=label,
                value=annotation.get("text") or annotation.get("trigger") or label,
                source_trace=source_trace,
                attributes={
                    "source_field": "deontic_modality",
                    "annotation": _json_safe_mapping(annotation),
                },
            )
        )
    return exports


def _temporal_records(
    record: PipelineRecord,
    source_trace: SourceTrace,
) -> list[ExtractionRecord]:
    exports: list[ExtractionRecord] = []
    for index, annotation in enumerate(record.temporal_expressions):
        label = _annotation_label(annotation, fallback="date")
        value = annotation.get("value") or annotation.get("text") or label
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "date", index),
                family=ExtractionFamily.DATE,
                label=label,
                value=value,
                normalized_value=annotation.get("value"),
                source_trace=source_trace,
                attributes={
                    "source_field": "temporal_expressions",
                    "annotation": _json_safe_mapping(annotation),
                },
            )
        )
    return exports


def _entity_records(
    record: PipelineRecord,
    source_trace: SourceTrace,
) -> list[ExtractionRecord]:
    exports: list[ExtractionRecord] = []
    for index, entity in enumerate(record.resolved_entities):
        label = str(entity.get("label") or entity.get("name") or entity.get("text") or "entity")
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "entity", index),
                family=ExtractionFamily.ENTITY,
                label=label,
                value=entity.get("text") or entity.get("name") or label,
                normalized_value=entity.get("qid") or entity.get("wikidata_id"),
                source_trace=source_trace,
                attributes={
                    "source_field": "resolved_entities",
                    "entity": _json_safe_mapping(entity),
                },
            )
        )
    return exports


def _amendment_records(
    record: PipelineRecord,
    source_trace: SourceTrace,
) -> list[ExtractionRecord]:
    exports: list[ExtractionRecord] = []
    for index, amendment in enumerate(record.amendments):
        label = str(amendment.get("type") or amendment.get("target_clause") or "amendment")
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "amendment", index),
                family=ExtractionFamily.AMENDMENT,
                label=label,
                value=amendment.get("text") or label,
                source_trace=source_trace,
                attributes={
                    "source_field": "amendments",
                    "amendment": _json_safe_mapping(amendment),
                },
            )
        )
    return exports


def _cross_reference_records(
    record: PipelineRecord,
    source_trace: SourceTrace,
) -> list[ExtractionRecord]:
    exports: list[ExtractionRecord] = []
    for index, citation in enumerate(record.nz_act_citations):
        exports.append(
            ExtractionRecord(
                record_id=_record_id(record, "cross_reference", index),
                family=ExtractionFamily.CROSS_REFERENCE,
                label="NZ Act citation",
                value=citation,
                normalized_value=_citation_path(record),
                source_trace=source_trace,
                attributes={"source_field": "nz_act_citations"},
            )
        )
    return exports


def _source_trace_for_record(
    record: PipelineRecord,
    *,
    retrieved_at: str,
    source_url_base: str,
) -> SourceTrace:
    text = record.raw_text.strip() or " "
    return SourceTrace(
        citation_path=_citation_path(record),
        source_sha256=source_sha256(text),
        source_url=f"{source_url_base.rstrip('/')}/{record.doc_id}",
        retrieved_at=retrieved_at,
        spans=(ExtractedSpan(start=0, end=len(text), text=text),),
    )


def _citation_path(record: PipelineRecord) -> str:
    return record.nz_act_citations[0] if record.nz_act_citations else record.doc_id


def _record_id(record: PipelineRecord, family: str, index: int) -> str:
    return f"nz:{_citation_path(record)}#{family}-{index}".replace(" ", "-").lower()


def _annotation_label(annotation: dict[str, Any], *, fallback: str) -> str:
    return str(
        annotation.get("label")
        or annotation.get("modality")
        or annotation.get("type")
        or annotation.get("kind")
        or fallback
    )


def _family_from_deontic(label: str) -> ExtractionFamily:
    normalised = label.lower()
    if "prohibit" in normalised or "forbid" in normalised or "must_not" in normalised:
        return ExtractionFamily.PROHIBITION
    if "permit" in normalised or "may" in normalised:
        return ExtractionFamily.PERMISSION
    if "power" in normalised:
        return ExtractionFamily.POWER
    return ExtractionFamily.OBLIGATION


def _family_from_legal_effect(value: str) -> ExtractionFamily:
    normalised = value.strip().lower().replace("-", "_").replace(" ", "_")
    family_values = {family.value: family for family in ExtractionFamily}
    return family_values.get(normalised, ExtractionFamily.RULES_AS_CODE)


def _json_safe_mapping(value: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow JSON-safe mapping for manifest attributes."""
    return {
        str(key): item
        for key, item in value.items()
        if item is None or isinstance(item, str | int | float | bool | list | dict)
    }
