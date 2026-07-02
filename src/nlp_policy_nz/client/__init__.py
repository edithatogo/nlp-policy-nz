"""First-class client SDK for the nlp-policy-nz API."""

from __future__ import annotations

from nlp_policy_nz.client.async_client import AsyncNLPPolicyNZClient
from nlp_policy_nz.client.models import (
    EmbedRequest,
    EmbedResponse,
    HealthResponse,
    ProcessRequest,
    ProcessResponse,
    SearchRequest,
    SearchResponse,
    VersionResponse,
)
from nlp_policy_nz.client.sync import NLPPolicyNZClient

__all__ = [
    "AsyncNLPPolicyNZClient",
    "EmbedRequest",
    "EmbedResponse",
    "HealthResponse",
    "NLPPolicyNZClient",
    "ProcessRequest",
    "ProcessResponse",
    "SearchRequest",
    "SearchResponse",
    "VersionResponse",
]
