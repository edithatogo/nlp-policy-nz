"""Lazy public exports for NZ legal NLP fine-tuning workflows."""

from __future__ import annotations

from importlib import import_module

_EXPORT_MODULES: dict[str, str] = {
    "ArchitectureCandidate": "nlp_policy_nz.training.eval_arch",
    "ArchitectureEvaluation": "nlp_policy_nz.training.eval_arch",
    "ArchitectureMetrics": "nlp_policy_nz.training.eval_arch",
    "IsaacusAccessGate": "nlp_policy_nz.training.isaacus_adapter",
    "IsaacusDatasetManifest": "nlp_policy_nz.training.isaacus_adapter",
    "IsaacusModelManifest": "nlp_policy_nz.training.isaacus_adapter",
    "IsaacusRecord": "nlp_policy_nz.training.isaacus_adapter",
    "IsaacusToolManifest": "nlp_policy_nz.training.isaacus_adapter",
    "MaskedLanguageModelingCollator": "nlp_policy_nz.training.data",
    "MlebNzQuery": "nlp_policy_nz.training.isaacus_adapter",
    "ModelTrainingConfig": "nlp_policy_nz.training.trainers",
    "QLoRAConfig": "nlp_policy_nz.training.trainers",
    "Track13EvidenceReport": "nlp_policy_nz.training.track13_evidence",
    "SilverConsensus": "nlp_policy_nz.training.track13_silver",
    "OntologyConcept": "nlp_policy_nz.training.track13_silver",
    "SilverVote": "nlp_policy_nz.training.track13_silver",
    "Track20EvidenceReport": "nlp_policy_nz.training.track20_evidence",
    "Track21EvidenceReport": "nlp_policy_nz.training.track21_evidence",
    "Track22EvidenceReport": "nlp_policy_nz.training.track22_evidence",
    "TrainingExample": "nlp_policy_nz.training.data",
    "TrainingHyperparameters": "nlp_policy_nz.training.trainers",
    "TrainingJobSpec": "nlp_policy_nz.training.trainers",
    "TrainingSplitConfig": "nlp_policy_nz.training.data",
    "TrainingSplits": "nlp_policy_nz.training.data",
    "build_training_examples": "nlp_policy_nz.training.data",
    "classification_prf": "nlp_policy_nz.training.eval",
    "create_legal_bert_argument_component_job": "nlp_policy_nz.training.trainers",
    "create_legal_bert_mlm_job": "nlp_policy_nz.training.trainers",
    "create_legal_bert_stance_job": "nlp_policy_nz.training.trainers",
    "create_mlm_collator": "nlp_policy_nz.training.data",
    "create_qlora_job": "nlp_policy_nz.training.trainers",
    "default_architecture_registry": "nlp_policy_nz.training.eval_arch",
    "default_isaacus_datasets": "nlp_policy_nz.training.isaacus_adapter",
    "default_isaacus_models": "nlp_policy_nz.training.isaacus_adapter",
    "default_isaacus_tools": "nlp_policy_nz.training.isaacus_adapter",
    "evaluate_track13_acceptance": "nlp_policy_nz.training.track13_evidence",
    "evaluate_track20_acceptance": "nlp_policy_nz.training.track20_evidence",
    "evaluate_track21_acceptance": "nlp_policy_nz.training.track21_evidence",
    "evaluate_track22_acceptance": "nlp_policy_nz.training.track22_evidence",
    "exact_match": "nlp_policy_nz.training.eval",
    "make_nz_mleb_query": "nlp_policy_nz.training.isaacus_adapter",
    "maori_token_integrity": "nlp_policy_nz.training.eval",
    "normalize_isaacus_record": "nlp_policy_nz.training.isaacus_adapter",
    "normalize_isaacus_records": "nlp_policy_nz.training.isaacus_adapter",
    "pareto_frontier": "nlp_policy_nz.training.eval_arch",
    "prepare_training_splits": "nlp_policy_nz.training.data",
    "rank_architectures": "nlp_policy_nz.training.eval_arch",
    "recommend_architecture": "nlp_policy_nz.training.eval_arch",
    "render_architecture_report": "nlp_policy_nz.training.eval_arch",
    "render_isaacus_integration_report": "nlp_policy_nz.training.isaacus_adapter",
    "render_isaacus_manifest_json": "nlp_policy_nz.training.isaacus_adapter",
    "render_track13_evidence_markdown": "nlp_policy_nz.training.track13_evidence",
    "aggregate_silver_votes": "nlp_policy_nz.training.track13_silver",
    "discover_provider_availability": "nlp_policy_nz.training.track13_silver",
    "match_ontology_concepts": "nlp_policy_nz.training.track13_silver",
    "ontology_bridge_vote": "nlp_policy_nz.training.track13_silver",
    "render_track20_evidence_markdown": "nlp_policy_nz.training.track20_evidence",
    "render_track21_evidence_markdown": "nlp_policy_nz.training.track21_evidence",
    "render_track22_evidence_markdown": "nlp_policy_nz.training.track22_evidence",
    "require_external_access": "nlp_policy_nz.training.isaacus_adapter",
    "to_pipeline_record": "nlp_policy_nz.training.isaacus_adapter",
    "token_f1": "nlp_policy_nz.training.eval",
    "track13_acceptance_contract": "nlp_policy_nz.training.track13_evidence",
    "track13_residual_external_gates": "nlp_policy_nz.training.track13_evidence",
    "track20_acceptance_contract": "nlp_policy_nz.training.track20_evidence",
    "track20_residual_external_gates": "nlp_policy_nz.training.track20_evidence",
    "track21_acceptance_contract": "nlp_policy_nz.training.track21_evidence",
    "track21_residual_external_gates": "nlp_policy_nz.training.track21_evidence",
    "track22_acceptance_contract": "nlp_policy_nz.training.track22_evidence",
    "track22_residual_external_gates": "nlp_policy_nz.training.track22_evidence",
}

__all__ = tuple(sorted(_EXPORT_MODULES))


def __getattr__(name: str) -> object:
    """Import public training helpers only when callers request them."""
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value

