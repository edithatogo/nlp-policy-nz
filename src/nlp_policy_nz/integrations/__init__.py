"""
Integrations Module.

Provides data loading and integration interfaces for external data sources
used in the NLP preprocessing pipeline, including:

- huggingface: Load datasets from the Hugging Face Hub (Hansard, legislation)
- zenodo: Zenodo Sandbox API integration for archival deposits
- data_registry: Centralised registry for dataset provenance and sovereignty
"""

from nlp_policy_nz.integrations.zenodo import (
    DepositError,
    ZENODO_SANDBOX_API_URL,
    ZENODO_TOKEN_ENV_VAR,
    create_sandbox_deposit,
    get_zenodo_token,
    publish_deposit,
    upload_file_to_deposit,
)
from nlp_policy_nz.integrations.data_registry import (
    DataRecord,
    DataSovereigntyRegistry,
)

__all__: list[str] = [
    # Zenodo
    "DepositError",
    "ZENODO_SANDBOX_API_URL",
    "ZENODO_TOKEN_ENV_VAR",
    "create_sandbox_deposit",
    "get_zenodo_token",
    "publish_deposit",
    "upload_file_to_deposit",
    # Data Registry
    "DataRecord",
    "DataSovereigntyRegistry",
    # Sub-modules
    "huggingface",
    "zenodo",
    "data_registry",
]
