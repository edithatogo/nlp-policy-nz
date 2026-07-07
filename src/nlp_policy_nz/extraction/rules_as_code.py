"""Batch rules-as-code candidate export helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import orjson

from nlp_policy_nz.axiom import DOCUMENT_TYPES, SourceSection
from nlp_policy_nz.extraction.schemas import (
    ExtractedSpan,
    ExtractionFamily,
    ExtractionManifest,
    ExtractionRecord,
    GapStatus,
    GapType,
    KnownGap,
    SourceTrace,
    extraction_manifest_from_records,
    load_extraction_manifest_json,
    render_extraction_manifest_json,
)
from nlp_policy_nz.extraction.source_inventory import (
    SourceInventoryManifest,
    SourceInventoryRecord,
    SourceInventoryStatus,
    default_source_inventory_manifest,
)
from nlp_policy_nz.ontology import (
    RulesAsCodeBridgeRecord,
    build_rules_as_code_bridge,
)


@dataclass(frozen=True, slots=True)
class RulesAsCodeCandidateBundle:
    """Deterministic candidate export bundle for rules-as-code handoff."""

    manifest: ExtractionManifest
    bridge_records: tuple[RulesAsCodeBridgeRecord, ...]
    source_inventory_manifest: SourceInventoryManifest | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a review-friendly summary of the candidate bundle."""
        return {
            "manifest": json.loads(render_extraction_manifest_json(self.manifest)),
            "bridge_records": [record.to_jsonld() for record in self.bridge_records],
        }


def build_rules_as_code_candidate_bundle_from_source_inventory(
    manifest: SourceInventoryManifest | None = None,
) -> RulesAsCodeCandidateBundle:
    """Build a batch candidate export from the fixture-bounded inventory."""
    resolved = manifest or default_source_inventory_manifest()
    fixture_rows = _load_fixture_rows(resolved)
    candidates = _build_candidates_from_inventory_rows(resolved.records, fixture_rows)
    return RulesAsCodeCandidateBundle(
        manifest=extraction_manifest_from_records(
            tuple(candidate.extraction_record for candidate in candidates),
            known_gaps=tuple(_known_gap_from_inventory_record(record) for record in resolved.records if record.status != "available"),
        ),
        bridge_records=tuple(candidate.bridge_record for candidate in candidates),
        source_inventory_manifest=resolved,
    )


def build_rules_as_code_candidate_bundle_from_extraction_manifest(
    manifest: ExtractionManifest,
) -> RulesAsCodeCandidateBundle:
    """Build a batch candidate export from a broad extraction manifest."""
    candidates = _build_candidates_from_extraction_manifest(manifest)
    return RulesAsCodeCandidateBundle(
        manifest=extraction_manifest_from_records(
            tuple(candidate.extraction_record for candidate in candidates),
            known_gaps=manifest.summary.known_gaps,
        ),
        bridge_records=tuple(candidate.bridge_record for candidate in candidates),
    )


def build_rules_as_code_candidate_bundle_from_pipeline_parquet(
    parquet_path: str | Path,
    *,
    retrieved_at: str,
    source_url_base: str = "pipeline://records",
) -> RulesAsCodeCandidateBundle:
    """Build a batch candidate export from pipeline Parquet output."""
    from nlp_policy_nz.extraction.exporter import extraction_manifest_from_pipeline_records
    from nlp_policy_nz.storage import load_from_parquet

    records = load_from_parquet(parquet_path)
    manifest = extraction_manifest_from_pipeline_records(
        records,
        retrieved_at=retrieved_at,
        source_url_base=source_url_base,
    )
    return build_rules_as_code_candidate_bundle_from_extraction_manifest(manifest)


def write_rules_as_code_candidate_bundle(
    bundle: RulesAsCodeCandidateBundle,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Write the batch candidate export artifacts to *output_dir*."""
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "rules_as_code_candidates.json"
    bridges_path = root / "rules_as_code_bridges.json"
    summary_path = root / "rules_as_code_candidates.md"
    manifest_path.write_text(render_extraction_manifest_json(bundle.manifest), encoding="utf-8")
    bridges_path.write_text(_render_bridge_array_json(bundle.bridge_records), encoding="utf-8")
    summary_path.write_text(_render_bundle_summary(bundle), encoding="utf-8")
    return {
        "rules_as_code_candidates.json": manifest_path,
        "rules_as_code_bridges.json": bridges_path,
        "rules_as_code_candidates.md": summary_path,
    }


def export_rules_as_code_candidates_from_source_inventory(
    output_dir: str | Path,
    manifest: SourceInventoryManifest | None = None,
) -> dict[str, Path]:
    """Build and write candidate artifacts from the fixture inventory."""
    bundle = build_rules_as_code_candidate_bundle_from_source_inventory(manifest)
    return write_rules_as_code_candidate_bundle(bundle, output_dir)


def export_rules_as_code_candidates_from_extraction_manifest(
    manifest_path: str | Path,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Build and write candidate artifacts from a stored extraction manifest."""
    manifest = load_extraction_manifest_json(manifest_path)
    bundle = build_rules_as_code_candidate_bundle_from_extraction_manifest(manifest)
    return write_rules_as_code_candidate_bundle(bundle, output_dir)


def export_rules_as_code_candidates_from_pipeline_parquet(
    parquet_path: str | Path,
    output_dir: str | Path,
    *,
    retrieved_at: str,
    source_url_base: str = "pipeline://records",
) -> dict[str, Path]:
    """Build and write candidate artifacts from pipeline Parquet rows."""
    bundle = build_rules_as_code_candidate_bundle_from_pipeline_parquet(
        parquet_path,
        retrieved_at=retrieved_at,
        source_url_base=source_url_base,
    )
    return write_rules_as_code_candidate_bundle(bundle, output_dir)


def _build_candidates_from_inventory_rows(
    inventory_records: tuple[SourceInventoryRecord, ...],
    fixture_rows: dict[str, dict[str, Any]],
) -> list[_Candidate]:
    candidates: list[_Candidate] = []
    for record in sorted(inventory_records, key=lambda item: (item.citation_path, item.inventory_id)):
        row = fixture_rows.get(record.inventory_id)
        if row is None:
            raise ValueError(f"missing fixture row for inventory record {record.inventory_id}")
        text = str(row.get("source_text", "")).strip()
        if not text:
            continue
        section = _section_from_inventory_row(record, row)
        review_status = _review_status_for_inventory_status(record.status)
        known_gap_ids = (record.known_gap_id,) if record.known_gap_id else ()
        candidates.append(
            _candidate_from_section(
                section,
                inventory_status=record.status,
                confidence=_confidence_for_inventory_status(record.status),
                review_status=review_status,
                known_gap_ids=known_gap_ids,
            )
        )
    return candidates


def _candidate_from_section(
    section: SourceSection,
    *,
    inventory_status: str,
    confidence: float,
    review_status: str,
    known_gap_ids: tuple[str, ...],
) -> _Candidate:
    bridge = build_rules_as_code_bridge(
        section,
        confidence=confidence,
        review_status=review_status,
        known_gap_ids=known_gap_ids,
    )
    return _Candidate(
        extraction_record=_candidate_extraction_record(
            section,
            bridge,
            inventory_status=inventory_status,
            confidence=confidence,
            review_status=review_status,
            known_gap_ids=known_gap_ids,
        ),
        bridge_record=bridge,
    )


def _build_candidates_from_extraction_manifest(
    manifest: ExtractionManifest,
) -> list[_Candidate]:
    grouped: dict[tuple[str, str], list[ExtractionRecord]] = {}
    for record in manifest.records:
        key = (record.source_trace.citation_path, record.source_trace.source_sha256)
        grouped.setdefault(key, []).append(record)
    candidates: list[_Candidate] = []
    for _, grouped_records in sorted(grouped.items()):
        source_record = _select_source_record(grouped_records)
        section = _section_from_extraction_record(source_record)
        review_status = _review_status_from_record(source_record)
        known_gap_ids = _known_gap_ids_from_record(source_record)
        confidence = source_record.confidence if source_record.confidence is not None else 1.0
        bridge = build_rules_as_code_bridge(
            section,
            confidence=confidence,
            review_status=review_status,
            known_gap_ids=known_gap_ids,
        )
        candidates.append(
            _Candidate(
                extraction_record=_candidate_extraction_record(
                    section,
                    bridge,
                    inventory_status=str(source_record.attributes.get("inventory_status", "manifest")),
                    confidence=confidence,
                    review_status=review_status,
                    known_gap_ids=known_gap_ids,
                ),
                bridge_record=bridge,
            )
        )
    return candidates


def _candidate_extraction_record(
    section: SourceSection,
    bridge: RulesAsCodeBridgeRecord,
    *,
    inventory_status: str,
    confidence: float,
    review_status: str,
    known_gap_ids: tuple[str, ...],
) -> ExtractionRecord:
    """Build a source-grounded rules-as-code extraction record."""
    reference = bridge.rulespec["rulespec_reference"]
    legal_effect = bridge.norm_semantics.legal_effect or "source_text"
    return ExtractionRecord(
        record_id=str(reference["durable_id"]),
        family=ExtractionFamily.RULES_AS_CODE,
        label=str(reference.get("concept") or legal_effect),
        value=str(reference["durable_id"]),
        normalized_value=bridge.norm_semantics.legal_effect,
        source_trace=_source_trace_from_section(section),
        confidence=confidence,
        attributes={
            "rulespec_id": reference["durable_id"],
            "rulespec_concept": reference.get("concept"),
            "inventory_status": inventory_status,
            "review_status": review_status,
            "known_gap_ids": list(known_gap_ids),
            "legal_effect": bridge.norm_semantics.legal_effect,
            "deontic_modality": bridge.norm_semantics.deontic_modality,
            "temporal_validity": bridge.temporal_validity.to_dict(),
            "source_citation_path": section.metadata.citation_path,
            "source_sha256": section.metadata.checksum_sha256,
            "source_url": section.metadata.source_url,
            "retrieved_at": section.metadata.retrieved_at,
        },
    )


def _section_from_inventory_row(
    record: SourceInventoryRecord,
    row: dict[str, Any],
) -> SourceSection:
    return SourceSection.from_text(
        str(row["source_text"]),
        citation_path=record.citation_path,
        jurisdiction=record.jurisdiction,
        document_type=_inventory_document_type(record.document_kind),  # type: ignore[arg-type]
        source_url=record.source_url,
        retrieved_at=record.retrieved_at,
        title=record.title,
        version_id=record.version,
        effective_date=record.effective_from,
        rights=record.rights_note,
        extra={
            "inventory_id": record.inventory_id,
            "source_type": record.source_type,
            "status": record.status,
            "known_gap_id": record.known_gap_id,
            "update_policy": record.update_policy,
            "notes": record.notes,
        },
    )


def _section_from_extraction_record(record: ExtractionRecord) -> SourceSection:
    text = "\n".join(span.text for span in record.source_trace.spans).strip()
    if not text:
        raise ValueError(f"source trace for {record.record_id} does not contain span text")
    source_url = str(record.attributes.get("source_url") or record.source_trace.source_url)
    retrieved_at = str(record.attributes.get("retrieved_at") or record.source_trace.retrieved_at)
    return SourceSection.from_text(
        text,
        citation_path=record.source_trace.citation_path,
        jurisdiction=str(record.attributes.get("jurisdiction", "NZ")),
        document_type=str(record.attributes.get("document_type", "act")),  # type: ignore[arg-type]
        source_url=source_url,
        retrieved_at=retrieved_at,
        title=str(record.attributes.get("title")) if record.attributes.get("title") else None,
        version_id=str(record.attributes.get("version_id")) if record.attributes.get("version_id") else None,
        effective_date=str(record.attributes.get("effective_date")) if record.attributes.get("effective_date") else None,
        rights=str(record.attributes.get("rights")) if record.attributes.get("rights") else None,
        extra={
            "source_family": record.family.value,
            "rulespec_id": record.attributes.get("rulespec_id"),
        },
    )


def _select_source_record(records: list[ExtractionRecord]) -> ExtractionRecord:
    """Return the most suitable record for source-grounded batch export."""
    ranked = sorted(
        records,
        key=lambda item: (
            0 if item.family == ExtractionFamily.RULES_AS_CODE else 1,
            item.record_id,
        ),
    )
    return ranked[0]


def _inventory_document_type(document_kind: str) -> str:
    """Map inventory document kinds onto supported source-section document types."""
    if document_kind in DOCUMENT_TYPES:
        return document_kind
    return "act"


def _known_gap_from_inventory_record(record: SourceInventoryRecord) -> KnownGap:
    """Convert one inventory gap into a rules-as-code known-gap ratchet."""
    gap = record.known_gap_id or f"{record.inventory_id}:{record.status}"
    return KnownGap(
        gap_id=gap,
        gap_type=_gap_type_for_inventory_status(record.status),
        family=ExtractionFamily.RULES_AS_CODE,
        citation_path=record.citation_path,
        description=record.notes or f"{record.document_kind} source is {record.status}.",
        status=GapStatus.KNOWN,
        owner="nlp-policy-nz",
    )


def _gap_type_for_inventory_status(status: SourceInventoryStatus) -> GapType:
    """Map inventory statuses to broad extraction gap categories."""
    if status == "available":
        return GapType.EXTRACTION
    if status == "redirected":
        return GapType.CORPUS
    if status in {"pdf_only", "malformed"}:
        return GapType.PARSER
    return GapType.CORPUS


def _review_status_for_inventory_status(status: SourceInventoryStatus) -> str:
    """Map inventory statuses to candidate review gates."""
    if status == "available":
        return "unreviewed"
    if status == "redirected":
        return "deferred"
    if status in {"pdf_only", "malformed"}:
        return "deferred"
    return "blocked"


def _review_status_from_record(record: ExtractionRecord) -> str:
    """Return the best available review status from an extraction record."""
    value = record.attributes.get("review_status")
    if isinstance(value, str) and value.strip():
        normalized = value.strip().replace("-", "_").lower()
        if normalized in {"unreviewed", "reviewed", "blocked", "deferred"}:
            return normalized
    return "unreviewed"


def _known_gap_ids_from_record(record: ExtractionRecord) -> tuple[str, ...]:
    """Return known-gap identifiers encoded on an extraction record."""
    value = record.attributes.get("known_gap_ids")
    if isinstance(value, list):
        return tuple(str(item) for item in value if str(item).strip())
    if isinstance(value, tuple):
        return tuple(str(item) for item in value if str(item).strip())
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()


def _source_trace_from_section(section: SourceSection) -> SourceTrace:
    """Build an extraction source trace from a source section."""
    return SourceTrace(
        citation_path=section.metadata.citation_path,
        source_sha256=section.metadata.checksum_sha256,
        source_url=section.metadata.source_url,
        retrieved_at=section.metadata.retrieved_at,
        spans=(
            ExtractedSpan(
                start=0,
                end=len(section.text),
                text=section.text,
            ),
        ),
    )


def _confidence_for_inventory_status(status: SourceInventoryStatus) -> float:
    """Return a stable candidate confidence by inventory status."""
    return {
        "available": 0.98,
        "redirected": 0.85,
        "pdf_only": 0.75,
        "malformed": 0.6,
        "access_blocked": 0.35,
        "unavailable": 0.25,
    }[status]


def _load_fixture_rows(manifest: SourceInventoryManifest) -> dict[str, dict[str, Any]]:
    fixture_path = Path(manifest.fixture_path)
    if not fixture_path.is_absolute():
        fixture_path = Path(__file__).resolve().parents[3] / fixture_path
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    return {str(item["inventory_id"]): item for item in payload["records"]}


def _render_bridge_array_json(records: tuple[RulesAsCodeBridgeRecord, ...]) -> str:
    return orjson.dumps(
        [record.to_jsonld() for record in records],
        option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS,
    ).decode("utf-8") + "\n"


def _render_bundle_summary(bundle: RulesAsCodeCandidateBundle) -> str:
    known_gap_ids = sorted({gap.gap_id for gap in bundle.manifest.summary.known_gaps})
    bridge_count = len(bundle.bridge_records)
    available = len(bundle.manifest.records)
    return (
        "# Batch Rules-as-Code Candidate Export\n\n"
        f"- Candidate records: {available}\n"
        f"- Bridge records: {bridge_count}\n"
        f"- Known gaps: {len(known_gap_ids)}\n"
        f"- Gap ids: {', '.join(known_gap_ids) if known_gap_ids else 'none'}\n"
    )


@dataclass(frozen=True, slots=True)
class _Candidate:
    extraction_record: ExtractionRecord
    bridge_record: RulesAsCodeBridgeRecord
