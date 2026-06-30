"""Typed extraction records for source-grounded legislative outputs."""

from __future__ import annotations

from nlp_policy_nz.extraction.catalog import (
    CatalogRun,
    CatalogStalenessReport,
    initialise_extraction_catalog,
    list_catalog_runs,
    report_catalog_source_staleness,
    write_manifest_to_catalog,
)
from nlp_policy_nz.extraction.exporter import (
    export_extraction_manifest_from_parquet,
    extraction_manifest_from_pipeline_records,
)
from nlp_policy_nz.extraction.schemas import (
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

__all__ = [
    "CatalogRun",
    "CatalogStalenessReport",
    "ExtractedSpan",
    "ExtractionFamily",
    "ExtractionManifest",
    "ExtractionRecord",
    "ExtractionRunSummary",
    "ExtractorManifest",
    "ExtractorSpec",
    "GapStatus",
    "GapType",
    "KnownGap",
    "SourceTrace",
    "SourceTraceReport",
    "export_extraction_manifest_from_parquet",
    "extraction_manifest_from_pipeline_records",
    "extraction_manifest_from_records",
    "initialise_extraction_catalog",
    "list_catalog_runs",
    "render_extraction_manifest_json",
    "render_extractor_manifest_yaml",
    "report_catalog_source_staleness",
    "source_trace_reports_from_records",
    "write_manifest_to_catalog",
]
