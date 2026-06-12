"""
Integrations Module.

Provides data loading and integration interfaces for external data sources
used in the NLP preprocessing pipeline, including:

- huggingface: Load datasets from the Hugging Face Hub (Hansard, legislation)
- hf_uploader: Upload pipeline Parquet outputs to the Hugging Face Hub
- zenodo: Zenodo Sandbox API integration for archival deposits
- data_registry: Centralised registry for dataset provenance and sovereignty
"""

from nlp_policy_nz.integrations.data_registry import (
    DataRecord,
    DataSovereigntyRegistry,
)
from nlp_policy_nz.integrations.dataset_card import (
    generate_dataset_card,
    write_dataset_card,
)
from nlp_policy_nz.integrations.hf_uploader import (
    UploadError,
    create_dataset_repo,
    deploy_space,
    parquet_to_dataset,
    push_dataset_to_hub,
)
from nlp_policy_nz.integrations.release import ReleaseManager
from nlp_policy_nz.integrations.zenodo import (
    ZENODO_PRODUCTION_API_URL,
    ZENODO_PRODUCTION_TOKEN,
    ZENODO_SANDBOX_API_URL,
    ZENODO_TOKEN_ENV_VAR,
    DepositError,
    create_sandbox_deposit,
    get_zenodo_token,
    publish_deposit,
    upload_file_to_deposit,
)
from nlp_policy_nz.integrations.zenodo_archive import (
    ZenodoArchiver,
    archive_to_zenodo,
)

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
