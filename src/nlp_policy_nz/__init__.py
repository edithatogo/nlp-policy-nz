"""
nlp-policy-nz: Shared SOTA Legislative & Parliamentary NLP Core Engine.
Exposes modular XML ingestion, spaCy metadata injection, and target schema emitters.
"""

# Version 3 SOTA Framework Exports
from .universal_framework_v3 import (
    FrameworkConfig,
    UniversalIngestionEngine,
    get_ingestion_engine,
    MetaExtensionRegistry,
    ModularSpaCyBridgeComponentV3,
    TargetSchemaEmitter,
    SOTAPipelineVisualizer,
    run_framework as run_nlp_pipeline
)

__all__ = [
    "FrameworkConfig",
    "UniversalIngestionEngine",
    "get_ingestion_engine",
    "MetaExtensionRegistry",
    "ModularSpaCyBridgeComponentV3",
    "TargetSchemaEmitter",
    "SOTAPipelineVisualizer",
    "run_nlp_pipeline",
]
