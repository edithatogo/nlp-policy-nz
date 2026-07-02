"""Typed request and response models for the API client SDK."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health payload returned by the API."""

    status: str
    pipeline_status: str
    db_connected: bool
    model_loaded: bool
    model_name: str
    version: str
    last_run_timestamp: str | None = None


class VersionResponse(BaseModel):
    """Version metadata returned by the API."""

    version: str
    build_timestamp: str
    commit_sha: str
    dataset_revision: str


class EmbedRequest(BaseModel):
    """Embedding request payload."""

    texts: list[str] = Field(min_length=1)


class EmbedResponse(BaseModel):
    """Embedding response payload."""

    embeddings: list[list[float]]
    model_name: str
    dimension: int
    count: int
    elapsed_seconds: float


class SearchRequest(BaseModel):
    """Search request payload."""

    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
    db_path: str = "./lancedb_data"


class SearchResponse(BaseModel):
    """Search response payload."""

    results: list[dict[str, Any]]
    query: str
    count: int
    elapsed_seconds: float


class ProcessRequest(BaseModel):
    """Process request payload."""

    input: str = Field(min_length=1)
    source: str = Field(default="legislation", pattern=r"^(legislation|hansard)$")
    generate_embeddings: bool = False


class ProcessResponse(BaseModel):
    """Process response payload."""

    records: list[dict[str, Any]]
    source: str
    count: int
    output_path: str | None = None
    elapsed_seconds: float


__all__ = [
    "EmbedRequest",
    "EmbedResponse",
    "HealthResponse",
    "ProcessRequest",
    "ProcessResponse",
    "SearchRequest",
    "SearchResponse",
    "VersionResponse",
]
