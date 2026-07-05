"""Typed extraction records for source-grounded legislative outputs."""

from __future__ import annotations

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
    "render_source_inventory_json",
    "render_source_inventory_markdown",
    "validate_source_inventory_manifest",
    "write_source_inventory_artifacts",
    "write_source_inventory_parquet",
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
    "SourceInventoryGapStatus",
    "SourceInventoryGapType",
    "SourceInventoryKnownGap",
    "SourceInventoryLiveProbeReport",
    "SourceInventoryManifest",
    "SourceInventoryRecord",
    "SourceInventorySummary",
    "SourceTrace",
    "SourceTraceReport",
    "build_source_inventory_rows",
    "default_source_inventory_manifest",
    "detect_source_inventory_live_probe_report",
    "export_extraction_manifest_from_parquet",
    "extraction_manifest_from_pipeline_records",
    "extraction_manifest_from_records",
    "initialise_extraction_catalog",
    "list_catalog_runs",
    "render_extraction_manifest_json",
    "render_extractor_manifest_yaml",
    "render_source_inventory_json",
    "render_source_inventory_markdown",
    "report_catalog_source_staleness",
    "source_trace_reports_from_records",
    "validate_source_inventory_manifest",
    "write_manifest_to_catalog",
    "write_source_inventory_artifacts",
    "write_source_inventory_parquet",
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
    if name in _SOURCE_INVENTORY_EXPORTS:
        module = import_module("nlp_policy_nz.extraction.source_inventory")
        return getattr(module, name)
    raise AttributeError(f"module 'nlp_policy_nz.extraction' has no attribute {name!r}")
