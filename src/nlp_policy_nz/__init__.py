"""
nlp-policy-nz: Shared SOTA Legislative & Parliamentary NLP Core Engine.
Exposes modular XML ingestion, spaCy metadata injection, and target schema emitters.
"""

# Version 3 SOTA Framework Exports
from .universal_framework_v3 import (
    FrameworkConfig,
    MetaExtensionRegistry,
    ModularSpaCyBridgeComponentV3,
    SOTAPipelineVisualizer,
    TargetSchemaEmitter,
    UniversalIngestionEngine,
    get_ingestion_engine,
    run_framework as run_nlp_pipeline,
)

__all__ = [
    "FrameworkConfig",
    "MetaExtensionRegistry",
    "ModularSpaCyBridgeComponentV3",
    "SOTAPipelineVisualizer",
    "TargetSchemaEmitter",
    "UniversalIngestionEngine",
    "get_ingestion_engine",
    "run_nlp_pipeline",
]
