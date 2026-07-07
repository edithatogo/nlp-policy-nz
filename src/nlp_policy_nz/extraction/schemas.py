"""Pydantic 2 schemas for broad source-grounded legislation extraction."""

from __future__ import annotations

from collections import Counter
from enum import StrEnum
from pathlib import Path
from typing import Any

import orjson
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ExtractionFamily(StrEnum):
    """Supported legislation extraction output families."""

    DEFINITION = "definition"
    OBLIGATION = "obligation"
    PROHIBITION = "prohibition"
    PERMISSION = "permission"
    POWER = "power"
    CONDITION = "condition"
    EXCEPTION = "exception"
    ELIGIBILITY = "eligibility"
    THRESHOLD = "threshold"
    DATE = "date"
    ENTITY = "entity"
    AMENDMENT = "amendment"
    COMMENCEMENT = "commencement"
    REPEAL = "repeal"
    CROSS_REFERENCE = "cross_reference"
    PENALTY = "penalty"
    DELEGATION = "delegation"
    REVIEW_RIGHT = "review_right"
    RULES_AS_CODE = "rules_as_code"


class GapStatus(StrEnum):
    """Known-gap lifecycle status for extraction ratchets."""

    KNOWN = "known"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class GapType(StrEnum):
    """Known-gap categories for broad extraction coverage."""

    CORPUS = "corpus"
    PARSER = "parser"
    EXTRACTION = "extraction"
    VALIDATION = "validation"


class ExtractorSpec(BaseModel):
    """Versioned extractor manifest entry for one output family."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    extractor_id: str = Field(min_length=1)
    family: ExtractionFamily
    version: str = Field(min_length=1)
    description: str = Field(min_length=1)
    produces: tuple[str, ...] = Field(default_factory=tuple)
    depends_on: tuple[ExtractionFamily, ...] = Field(default_factory=tuple)

    @field_validator("produces")
    @classmethod
    def _validate_outputs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("produces must contain at least one output field")
        if any(not item.strip() for item in value):
            raise ValueError("produces entries must be non-empty")
        return value


class ExtractedSpan(BaseModel):
    """Character span in normalized source text."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    start: int = Field(ge=0)
    end: int = Field(gt=0)
    text: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_span_order(self) -> ExtractedSpan:
        if self.end <= self.start:
            raise ValueError("end must be greater than start")
        return self


class SourceTrace(BaseModel):
    """Checksum-pinned source locator for one extracted record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    citation_path: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_url: str = Field(min_length=1)
    retrieved_at: str = Field(min_length=1)
    spans: tuple[ExtractedSpan, ...] = Field(default_factory=tuple)


class ExtractionRecord(BaseModel):
    """One normalized extraction from source legislation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    record_id: str = Field(min_length=1)
    family: ExtractionFamily
    label: str = Field(min_length=1)
    value: str | int | float | bool | None = None
    normalized_value: str | int | float | bool | None = None
    source_trace: SourceTrace
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("attributes")
    @classmethod
    def _validate_attribute_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        for key in value:
            if not key.strip():
                raise ValueError("attribute keys must be non-empty")
        return value


class KnownGap(BaseModel):
    """Ratchet item for known extraction coverage or validation debt."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    gap_id: str = Field(min_length=1)
    gap_type: GapType
    family: ExtractionFamily | None = None
    citation_path: str | None = None
    description: str = Field(min_length=1)
    status: GapStatus = GapStatus.KNOWN
    owner: str | None = None


class SourceTraceReport(BaseModel):
    """Source-to-output audit report for a set of extracted records."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    citation_path: str = Field(min_length=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    record_ids: tuple[str, ...] = Field(default_factory=tuple)
    covered_spans: tuple[ExtractedSpan, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_has_records_or_spans(self) -> SourceTraceReport:
        if not self.record_ids and not self.covered_spans:
            raise ValueError("trace reports must include at least one record or span")
        return self


class ExtractionRunSummary(BaseModel):
    """Summary counts and coverage signals for an extraction run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_records: int = Field(ge=0)
    families: dict[ExtractionFamily, int] = Field(default_factory=dict)
    citation_paths: tuple[str, ...] = Field(default_factory=tuple)
    known_gaps: tuple[KnownGap, ...] = Field(default_factory=tuple)


class ExtractorManifest(BaseModel):
    """Manifest describing extractors that can produce output families."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    extractors: tuple[ExtractorSpec, ...]
    known_gaps: tuple[KnownGap, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_unique_extractors(self) -> ExtractorManifest:
        ids = [extractor.extractor_id for extractor in self.extractors]
        if len(ids) != len(set(ids)):
            raise ValueError("extractor IDs must be unique")
        return self


class ExtractionManifest(BaseModel):
    """Portable extraction manifest for downstream consumers."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    producer: str = "nlp-policy-nz"
    records: tuple[ExtractionRecord, ...]
    summary: ExtractionRunSummary
    trace_reports: tuple[SourceTraceReport, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_summary_matches_records(self) -> ExtractionManifest:
        if self.summary.total_records != len(self.records):
            raise ValueError("summary.total_records must match records length")
        expected = Counter(record.family for record in self.records)
        if dict(expected) != self.summary.families:
            raise ValueError("summary.families must match record family counts")
        return self


def load_extraction_manifest_json(path: str | Path) -> ExtractionManifest:
    """Load an extraction manifest from deterministic JSON."""
    src = Path(path).resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Extraction manifest not found: {src}")
    return ExtractionManifest.model_validate_json(src.read_text(encoding="utf-8"))


def extraction_manifest_from_records(
    records: list[ExtractionRecord] | tuple[ExtractionRecord, ...],
    *,
    known_gaps: tuple[KnownGap, ...] = (),
) -> ExtractionManifest:
    """Build a manifest with deterministic summary fields from records."""
    normalized_records = tuple(records)
    families = dict(Counter(record.family for record in normalized_records))
    citation_paths = tuple(
        sorted({record.source_trace.citation_path for record in normalized_records})
    )
    summary = ExtractionRunSummary(
        total_records=len(normalized_records),
        families=families,
        citation_paths=citation_paths,
        known_gaps=known_gaps,
    )
    return ExtractionManifest(
        records=normalized_records,
        summary=summary,
        trace_reports=source_trace_reports_from_records(normalized_records),
    )


def source_trace_reports_from_records(
    records: tuple[ExtractionRecord, ...],
) -> tuple[SourceTraceReport, ...]:
    """Build source-to-output trace reports grouped by citation and source hash."""
    grouped: dict[tuple[str, str], list[ExtractionRecord]] = {}
    for record in records:
        key = (record.source_trace.citation_path, record.source_trace.source_sha256)
        grouped.setdefault(key, []).append(record)
    reports: list[SourceTraceReport] = []
    for (citation_path, source_sha256), grouped_records in sorted(grouped.items()):
        spans = tuple(span for record in grouped_records for span in record.source_trace.spans)
        reports.append(
            SourceTraceReport(
                citation_path=citation_path,
                source_sha256=source_sha256,
                record_ids=tuple(record.record_id for record in grouped_records),
                covered_spans=spans,
            )
        )
    return tuple(reports)


def render_extraction_manifest_json(manifest: ExtractionManifest) -> str:
    """Render an extraction manifest as deterministic JSON."""
    payload = manifest.model_dump(mode="json")
    return orjson.dumps(payload, option=orjson.OPT_SORT_KEYS).decode("utf-8") + "\n"


def render_extractor_manifest_yaml(manifest: ExtractorManifest) -> str:
    """Render an extractor manifest as stable YAML for review and handoff."""
    payload = manifest.model_dump(mode="json")
    return yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)
