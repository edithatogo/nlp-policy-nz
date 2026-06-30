from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from nlp_policy_nz.extraction import (
    ExtractedSpan,
    ExtractionFamily,
    ExtractionManifest,
    ExtractionRecord,
    ExtractionRunSummary,
    ExtractorManifest,
    ExtractorSpec,
    GapStatus,
    GapType,
    KnownGap,
    SourceTrace,
    SourceTraceReport,
    extraction_manifest_from_records,
    render_extraction_manifest_json,
    render_extractor_manifest_yaml,
    source_trace_reports_from_records,
)


def _source_trace() -> SourceTrace:
    return SourceTrace(
        citation_path="nz/statutes/example-act/2026/10",
        source_sha256="0" * 64,
        source_url="https://legislation.govt.nz/example-act/section/10",
        retrieved_at="2026-06-30T00:00:00Z",
        spans=(ExtractedSpan(start=0, end=24, text="A person must comply."),),
    )


def test_extraction_manifest_summarises_broad_legislative_outputs() -> None:
    known_gap = KnownGap(
        gap_id="definitions-gap",
        gap_type=GapType.EXTRACTION,
        family=ExtractionFamily.DEFINITION,
        citation_path="nz/statutes/example-act/2026/10",
        description="Definition extractor is not yet connected to this fixture.",
    )
    records = (
        ExtractionRecord(
            record_id="nz:statutes/example-act/2026/10#obligation",
            family=ExtractionFamily.OBLIGATION,
            label="information duty",
            value="A person must provide information.",
            source_trace=_source_trace(),
            attributes={"deontic_trigger": "must"},
        ),
        ExtractionRecord(
            record_id="nz:statutes/example-act/2026/10#rules_as_code",
            family=ExtractionFamily.RULES_AS_CODE,
            label="candidate RuleSpec bridge",
            source_trace=_source_trace(),
            confidence=0.8,
            attributes={"rulespec_id": "nz:statutes/example-act/2026/10#obligation"},
        ),
    )

    manifest = extraction_manifest_from_records(records, known_gaps=(known_gap,))
    payload = json.loads(render_extraction_manifest_json(manifest))

    assert manifest.summary.total_records == 2
    assert manifest.summary.families[ExtractionFamily.OBLIGATION] == 1
    assert manifest.summary.families[ExtractionFamily.RULES_AS_CODE] == 1
    assert manifest.summary.citation_paths == ("nz/statutes/example-act/2026/10",)
    assert manifest.summary.known_gaps == (known_gap,)
    assert manifest.trace_reports[0].record_ids == (
        "nz:statutes/example-act/2026/10#obligation",
        "nz:statutes/example-act/2026/10#rules_as_code",
    )
    assert payload["producer"] == "nlp-policy-nz"
    assert payload["records"][0]["source_trace"]["source_sha256"] == "0" * 64


def test_extraction_schema_rejects_invalid_source_trace_and_summary() -> None:
    with pytest.raises(ValidationError, match="source_sha256"):
        SourceTrace(
            citation_path="nz/statutes/example-act/2026/10",
            source_sha256="ABC",
            source_url="https://legislation.govt.nz/example-act/section/10",
            retrieved_at="2026-06-30T00:00:00Z",
        )

    record = ExtractionRecord(
        record_id="nz:statutes/example-act/2026/10#obligation",
        family=ExtractionFamily.OBLIGATION,
        label="information duty",
        source_trace=_source_trace(),
    )

    with pytest.raises(ValidationError, match=r"summary\.total_records"):
        ExtractionManifest(
            records=(record,),
            summary=ExtractionRunSummary(
                total_records=2, families={ExtractionFamily.OBLIGATION: 1}
            ),
        )


def test_extracted_span_requires_forward_nonempty_range() -> None:
    with pytest.raises(ValidationError, match="end must be greater"):
        ExtractedSpan(start=10, end=10, text="bad")


def test_extractor_manifest_renders_stable_yaml_and_rejects_duplicates() -> None:
    manifest = ExtractorManifest(
        extractors=(
            ExtractorSpec(
                extractor_id="obligation-v1",
                family=ExtractionFamily.OBLIGATION,
                version="0.1.0",
                description="Detects deontic obligation triggers.",
                produces=("label", "source_trace", "attributes.deontic_trigger"),
            ),
            ExtractorSpec(
                extractor_id="rules-as-code-v1",
                family=ExtractionFamily.RULES_AS_CODE,
                version="0.1.0",
                description="Exports candidate durable IDs for RuleSpec review.",
                produces=("record_id", "attributes.rulespec_id"),
                depends_on=(ExtractionFamily.OBLIGATION,),
            ),
        ),
        known_gaps=(
            KnownGap(
                gap_id="date-parser-gap",
                gap_type=GapType.PARSER,
                family=ExtractionFamily.DATE,
                description="Date normalization still needs fixture coverage.",
                status=GapStatus.IN_PROGRESS,
            ),
        ),
    )

    rendered = render_extractor_manifest_yaml(manifest)

    assert "extractor_id: obligation-v1" in rendered
    assert "family: rules_as_code" in rendered
    assert "gap_id: date-parser-gap" in rendered

    with pytest.raises(ValidationError, match="extractor IDs must be unique"):
        ExtractorManifest(
            extractors=(
                ExtractorSpec(
                    extractor_id="duplicate",
                    family=ExtractionFamily.ENTITY,
                    version="0.1.0",
                    description="First extractor.",
                    produces=("label",),
                ),
                ExtractorSpec(
                    extractor_id="duplicate",
                    family=ExtractionFamily.DATE,
                    version="0.1.0",
                    description="Second extractor.",
                    produces=("label",),
                ),
            )
        )


def test_source_trace_reports_group_records_by_source_identity() -> None:
    first = ExtractionRecord(
        record_id="nz:statutes/example-act/2026/10#obligation",
        family=ExtractionFamily.OBLIGATION,
        label="information duty",
        source_trace=_source_trace(),
    )
    second = ExtractionRecord(
        record_id="nz:statutes/example-act/2026/10#definition",
        family=ExtractionFamily.DEFINITION,
        label="person",
        source_trace=SourceTrace(
            citation_path="nz/statutes/example-act/2026/10",
            source_sha256="0" * 64,
            source_url="https://legislation.govt.nz/example-act/section/10",
            retrieved_at="2026-06-30T00:00:00Z",
            spans=(ExtractedSpan(start=40, end=52, text="person means"),),
        ),
    )

    reports = source_trace_reports_from_records((first, second))

    assert len(reports) == 1
    assert reports[0].citation_path == "nz/statutes/example-act/2026/10"
    assert reports[0].record_ids == (
        "nz:statutes/example-act/2026/10#obligation",
        "nz:statutes/example-act/2026/10#definition",
    )
    assert [span.text for span in reports[0].covered_spans] == [
        "A person must comply.",
        "person means",
    ]


def test_source_trace_report_requires_record_or_span() -> None:
    with pytest.raises(ValidationError, match="at least one record or span"):
        SourceTraceReport(
            citation_path="nz/statutes/example-act/2026/10",
            source_sha256="0" * 64,
        )
