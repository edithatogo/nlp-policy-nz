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
from importlib import import_module

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
_RULES_AS_CODE_EXPORTS = {
    "RulesAsCodeCandidateBundle",
    "build_rules_as_code_candidate_bundle_from_extraction_manifest",
    "build_rules_as_code_candidate_bundle_from_pipeline_parquet",
    "build_rules_as_code_candidate_bundle_from_source_inventory",
    "export_rules_as_code_candidates_from_extraction_manifest",
    "export_rules_as_code_candidates_from_pipeline_parquet",
    "export_rules_as_code_candidates_from_source_inventory",
    "write_rules_as_code_candidate_bundle",
}
_SOURCE_INVENTORY_EXPORTS = {
    "SourceInventoryGapStatus",
    "SourceInventoryGapType",
    "SourceInventoryKnownGap",
    "SourceInventoryLiveProbeReport",
    "SourceInventoryManifest",
    "SourceInventoryRecord",
    "SourceInventorySummary",
    "build_source_inventory_rows",
    "default_source_inventory_manifest",
    "detect_source_inventory_live_probe_report",
    "load_source_inventory_manifest_json",
    "render_source_inventory_json",
    "render_source_inventory_markdown",
    "validate_source_inventory_manifest",
    "write_source_inventory_artifacts",
    "write_source_inventory_parquet",
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
    "write_rules_as_code_candidate_bundle",
    "write_source_inventory_artifacts",
    "write_source_inventory_parquet",
    "AccessClass",
    "AcquisitionMode",
    "HathiArchiveItem",
    "HathiArchiveRegistry",
    "HathiDatasetDescriptor",
    "HathiWorkItem",
    "HathiWorkManifest",
    "HathiWorkShard",
    "PublicationDecision",
    "build_work_manifest",
    "load_archive_registry",
    "render_work_manifest_json",
    "render_hathi_json_schema",
    "validate_curated_seed_count",
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
    if name in _RULES_AS_CODE_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.rules_as_code")
        return getattr(module, name)
    if name in _SOURCE_INVENTORY_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.source_inventory")
        return getattr(module, name)
    if name in _HATHI_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.hathi_ingestion")
        return getattr(module, name)
    raise AttributeError(f"module 'nlp_policy_nz.extraction' has no attribute {name!r}")
