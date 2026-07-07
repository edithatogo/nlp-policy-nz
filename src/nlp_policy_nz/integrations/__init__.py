"""Integrations Module.

Provides data loading and integration interfaces for external data sources
used in the NLP preprocessing pipeline, including:

- huggingface: Load datasets from the Hugging Face Hub (Hansard, legislation)
- hf_uploader: Upload pipeline Parquet outputs to the Hugging Face Hub
- zenodo: Zenodo Sandbox API integration for archival deposits
- data_registry: Centralised registry for dataset provenance and sovereignty
"""

from __future__ import annotations

from importlib import import_module

__all__: list[str] = [
    "ZENODO_PRODUCTION_API_URL",
    "ZENODO_PRODUCTION_TOKEN",
    "ZENODO_SANDBOX_API_URL",
    "ZENODO_TOKEN_ENV_VAR",
    "DataRecord",
    "DataSovereigntyRegistry",
    "DepositError",
    "ReleaseManager",
    "UploadError",
    "ZenodoArchiver",
    "archive_to_zenodo",
    "create_dataset_repo",
    "create_sandbox_deposit",
    "data_registry",
    "deploy_space",
    "generate_dataset_card",
    "get_zenodo_token",
    "huggingface",
    "parquet_to_dataset",
    "publish_deposit",
    "push_dataset_to_hub",
    "upload_file_to_deposit",
    "write_dataset_card",
    "zenodo",
]

_EXPORTS: dict[str, str] = {
    "DataRecord": "nlp_policy_nz.integrations.data_registry",
    "DataSovereigntyRegistry": "nlp_policy_nz.integrations.data_registry",
    "generate_dataset_card": "nlp_policy_nz.integrations.dataset_card",
    "write_dataset_card": "nlp_policy_nz.integrations.dataset_card",
    "UploadError": "nlp_policy_nz.integrations.hf_uploader",
    "create_dataset_repo": "nlp_policy_nz.integrations.hf_uploader",
    "deploy_space": "nlp_policy_nz.integrations.hf_uploader",
    "parquet_to_dataset": "nlp_policy_nz.integrations.hf_uploader",
    "push_dataset_to_hub": "nlp_policy_nz.integrations.hf_uploader",
    "ReleaseManager": "nlp_policy_nz.integrations.release",
    "ZENODO_PRODUCTION_API_URL": "nlp_policy_nz.integrations.zenodo",
    "ZENODO_PRODUCTION_TOKEN": "nlp_policy_nz.integrations.zenodo",
    "ZENODO_SANDBOX_API_URL": "nlp_policy_nz.integrations.zenodo",
    "ZENODO_TOKEN_ENV_VAR": "nlp_policy_nz.integrations.zenodo",
    "DepositError": "nlp_policy_nz.integrations.zenodo",
    "create_sandbox_deposit": "nlp_policy_nz.integrations.zenodo",
    "get_zenodo_token": "nlp_policy_nz.integrations.zenodo",
    "publish_deposit": "nlp_policy_nz.integrations.zenodo",
    "upload_file_to_deposit": "nlp_policy_nz.integrations.zenodo",
    "ZenodoArchiver": "nlp_policy_nz.integrations.zenodo_archive",
    "archive_to_zenodo": "nlp_policy_nz.integrations.zenodo_archive",
}


def __getattr__(name: str) -> object:
    """Lazily resolve integration helpers to avoid optional imports on CLI-only paths."""
    if name == "data_registry":
        return import_module("nlp_policy_nz.integrations.data_registry")
    if name == "huggingface":
        return import_module("nlp_policy_nz.integrations.huggingface")
    if name == "zenodo":
        return import_module("nlp_policy_nz.integrations.zenodo")
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(module_path)
    return getattr(module, name)
