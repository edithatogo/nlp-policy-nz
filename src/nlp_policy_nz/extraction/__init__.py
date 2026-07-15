"""Typed extraction records for source-grounded legislative outputs."""

from __future__ import annotations

from importlib import import_module

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
from nlp_policy_nz.extraction.foio_adapter import (
    FoioArchiveBundle,
    FoioArchiveSnapshot,
    FoioEvaluationFixture,
    FoioEvaluationReport,
    FoioLabelMetrics,
    build_foio_archive_bundle,
    compare_foio_baseline,
    evaluate_foio_candidates,
    evaluate_foio_fixture,
    load_foio_evaluation_fixture,
    render_foio_archive_bundle_json,
    render_foio_evaluation_json,
)
from nlp_policy_nz.extraction.foio_au_adapter import (
    AustralianJurisdiction,
    AustralianRoutingDecision,
    FoioAustralianArchiveBundle,
    FoioAustralianEvaluationFixture,
    FoioAustralianEvaluationReport,
    FoioAustralianJurisdictionEvaluation,
    FoioAustralianProfileSnapshot,
    build_australian_archive_bundle,
    evaluate_australian_candidates,
    evaluate_australian_fixture,
    load_australian_evaluation_fixture,
    render_australian_archive_bundle_json,
    render_australian_evaluation_json,
    route_australian_jurisdiction,
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

_SCHEMA_EXPORTS = {
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
    "load_extraction_manifest_json",
    "extraction_manifest_from_records",
    "render_extraction_manifest_json",
    "render_extractor_manifest_yaml",
    "source_trace_reports_from_records",
}
_CATALOG_EXPORTS = {
    "CatalogRun",
    "CatalogStalenessReport",
    "initialise_extraction_catalog",
    "list_catalog_runs",
    "report_catalog_source_staleness",
    "write_manifest_to_catalog",
}
_EXPORTER_EXPORTS = {
    "export_extraction_manifest_from_parquet",
    "extraction_manifest_from_pipeline_records",
}
_HATHI_EXPORTS = {
    "AccessClass",
    "AcquisitionMode",
    "HathiArchiveItem",
    "HathiArchiveRegistry",
    "HathiDatasetDescriptor",
    "HathiWorkItem",
    "HathiWorkManifest",
    "HathiWorkShard",
    "HATHI_CAPABILITY_REGISTRY",
    "PublicationDecision",
    "build_work_manifest",
    "load_archive_registry",
    "hathi_capability_registry",
    "render_work_manifest_json",
    "render_hathi_json_schema",
    "validate_curated_seed_count",
}

__all__ = [
    "AccessClass",
    "AcquisitionMode",
    "AustralianJurisdiction",
    "AustralianRoutingDecision",
    "CatalogRun",
    "CatalogStalenessReport",
    "ExtractedSpan",
    "ExtractionFamily",
    "ExtractionManifest",
    "ExtractionRecord",
    "ExtractionRunSummary",
    "ExtractorManifest",
    "ExtractorSpec",
    "FoioArchiveBundle",
    "FoioArchiveSnapshot",
    "FoioAustralianArchiveBundle",
    "FoioAustralianEvaluationFixture",
    "FoioAustralianEvaluationReport",
    "FoioAustralianJurisdictionEvaluation",
    "FoioAustralianProfileSnapshot",
    "FoioEvaluationFixture",
    "FoioEvaluationReport",
    "FoioLabelMetrics",
    "GapStatus",
    "GapType",
    "HathiArchiveItem",
    "HathiArchiveRegistry",
    "HathiDatasetDescriptor",
    "HathiWorkItem",
    "HathiWorkManifest",
    "HathiWorkShard",
    "KnownGap",
    "PublicationDecision",
    "SourceTrace",
    "SourceTraceReport",
    "build_australian_archive_bundle",
    "build_foio_archive_bundle",
    "build_work_manifest",
    "compare_foio_baseline",
    "evaluate_australian_candidates",
    "evaluate_australian_fixture",
    "evaluate_foio_candidates",
    "evaluate_foio_fixture",
    "export_extraction_manifest_from_parquet",
    "extraction_manifest_from_pipeline_records",
    "extraction_manifest_from_records",
    "initialise_extraction_catalog",
    "list_catalog_runs",
    "load_archive_registry",
    "load_australian_evaluation_fixture",
    "load_foio_evaluation_fixture",
    "render_australian_archive_bundle_json",
    "render_australian_evaluation_json",
    "render_extraction_manifest_json",
    "render_extractor_manifest_yaml",
    "render_foio_archive_bundle_json",
    "render_foio_evaluation_json",
    "render_hathi_json_schema",
    "render_work_manifest_json",
    "report_catalog_source_staleness",
    "route_australian_jurisdiction",
    "source_trace_reports_from_records",
    "validate_curated_seed_count",
    "write_manifest_to_catalog",
]


def __getattr__(name: str) -> object:
    """Lazily resolve extraction helpers on first access."""
    if name in _SCHEMA_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.schemas")
        return getattr(module, name)
    if name in _CATALOG_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.catalog")
        return getattr(module, name)
    if name in _EXPORTER_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.exporter")
        return getattr(module, name)
    if name in _HATHI_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.hathi_ingestion")
        return getattr(module, name)
    raise AttributeError(f"module 'nlp_policy_nz.extraction' has no attribute {name!r}")
