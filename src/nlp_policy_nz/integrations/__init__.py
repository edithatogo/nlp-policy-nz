"""
Integrations Module.

Provides data loading and integration interfaces for external data sources
used in the NLP preprocessing pipeline, including:

- huggingface: Load datasets from the Hugging Face Hub (Hansard, legislation)
- zenodo: Zenodo Sandbox API integration for archival deposits
- data_registry: Centralised registry for dataset provenance and sovereignty
"""

from nlp_policy_nz.integrations.data_registry import (
    DataRecord,
    DataSovereigntyRegistry,
)
from nlp_policy_nz.integrations.zenodo import (
    ZENODO_SANDBOX_API_URL,
    ZENODO_TOKEN_ENV_VAR,
    DepositError,
    create_sandbox_deposit,
    get_zenodo_token,
    publish_deposit,
    upload_file_to_deposit,
)

__all__: list[str] = [
    "ZENODO_SANDBOX_API_URL",
    "ZENODO_TOKEN_ENV_VAR",
    # Data Registry
    "DataRecord",
    "DataSovereigntyRegistry",
    # Zenodo
    "DepositError",
    "create_sandbox_deposit",
    "data_registry",
    "get_zenodo_token",
    # Sub-modules
    "huggingface",
    "publish_deposit",
    "upload_file_to_deposit",
    "zenodo",
]
