"""Shared SOTA Legislative & Parliamentary NLP Core Engine."""

from __future__ import annotations

from importlib import import_module

__version__ = "0.1.0"

_FRAMEWORK_EXPORTS: dict[str, tuple[str, str]] = {
    "build_corpus_statistics": (
        "nlp_policy_nz.analysis",
        "build_corpus_statistics",
    ),
    "build_analysis_artifact_bundle": (
        "nlp_policy_nz.analysis",
        "build_analysis_artifact_bundle",
    ),
    "build_graph_vector_network_analysis": (
        "nlp_policy_nz.analysis",
        "build_graph_vector_network_analysis",
    ),
    "build_nz_ontology_bundle": (
        "nlp_policy_nz.ontology",
        "build_nz_ontology_bundle",
    ),
    "build_nz_ontology_graph": (
        "nlp_policy_nz.ontology",
        "build_nz_ontology_graph",
    ),
    "build_publication_protocol": (
        "nlp_policy_nz.publication.protocol",
        "build_publication_protocol",
    ),
    "FrameworkConfig": ("nlp_policy_nz.universal_framework_v3", "FrameworkConfig"),
    "MetaExtensionRegistry": ("nlp_policy_nz.universal_framework_v3", "MetaExtensionRegistry"),
    "ModularSpaCyBridgeComponentV3": (
        "nlp_policy_nz.universal_framework_v3",
        "ModularSpaCyBridgeComponentV3",
    ),
    "SOTAPipelineVisualizer": ("nlp_policy_nz.universal_framework_v3", "SOTAPipelineVisualizer"),
    "TargetSchemaEmitter": ("nlp_policy_nz.universal_framework_v3", "TargetSchemaEmitter"),
    "UniversalIngestionEngine": (
        "nlp_policy_nz.universal_framework_v3",
        "UniversalIngestionEngine",
    ),
    "UnstructuredIngestionEngine": (
        "nlp_policy_nz.unstructured_ingestion",
        "UnstructuredIngestionEngine",
    ),
    "get_ingestion_engine": ("nlp_policy_nz.universal_framework_v3", "get_ingestion_engine"),
    "validate_nz_ontology_bundle": (
        "nlp_policy_nz.ontology",
        "validate_nz_ontology_bundle",
    ),
    "write_corpus_statistics_artifacts": (
        "nlp_policy_nz.analysis",
        "write_corpus_statistics_artifacts",
    ),
    "write_analysis_artifacts": (
        "nlp_policy_nz.analysis",
        "write_analysis_artifacts",
    ),
    "write_graph_vector_network_artifacts": (
        "nlp_policy_nz.analysis",
        "write_graph_vector_network_artifacts",
    ),
    "write_nz_ontology_artifacts": (
        "nlp_policy_nz.ontology",
        "write_nz_ontology_artifacts",
    ),
    "write_publication_protocol_artifacts": (
        "nlp_policy_nz.publication.protocol",
        "write_publication_protocol_artifacts",
    ),
}


def run_nlp_pipeline(*args: object, **kwargs: object) -> object:
    """Run the universal framework, importing optional parser deps only on use."""
    from nlp_policy_nz.universal_framework_v3 import run_framework

    return run_framework(*args, **kwargs)


def __getattr__(name: str) -> object:
    """Lazily resolve framework exports to keep package import lightweight."""
    if name not in _FRAMEWORK_EXPORTS:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    module_name, attribute_name = _FRAMEWORK_EXPORTS[name]
    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value


__all__ = [
    "FrameworkConfig",
    "MetaExtensionRegistry",
    "ModularSpaCyBridgeComponentV3",
    "SOTAPipelineVisualizer",
    "TargetSchemaEmitter",
    "UniversalIngestionEngine",
    "UnstructuredIngestionEngine",
    "__version__",
    "build_analysis_artifact_bundle",
    "build_corpus_statistics",
    "build_graph_vector_network_analysis",
    "build_nz_ontology_bundle",
    "build_nz_ontology_graph",
    "build_publication_protocol",
    "get_ingestion_engine",
    "run_nlp_pipeline",
    "validate_nz_ontology_bundle",
    "write_analysis_artifacts",
    "write_corpus_statistics_artifacts",
    "write_graph_vector_network_artifacts",
    "write_nz_ontology_artifacts",
    "write_publication_protocol_artifacts",
]
