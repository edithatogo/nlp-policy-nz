"""Async API client for nlp-policy-nz."""

# ruff: noqa: ANN401, D102, D105, PLR0911, TRY300, PYI034

from __future__ import annotations

import asyncio
import types
from collections.abc import Iterable
from typing import Any

import httpx
from pydantic import BaseModel

from nlp_policy_nz.client.errors import APIError, raise_for_problem
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
from nlp_policy_nz.client.sync import _BaseClient


class AsyncNLPPolicyNZClient(_BaseClient):
    """Asynchronous client for the public API."""

    def __init__(self, **kwargs: Any) -> None:
        transport = kwargs.pop("transport", None)
        super().__init__(**kwargs)
        self._client = httpx.AsyncClient(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            headers=self._headers(),
            transport=transport,
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncNLPPolicyNZClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None:
        await self.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._config.retry_attempts):
            try:
                response = await self._client.request(
                    method,
                    self._url(path),
                    json=json,
                    headers=self._headers(),
                )
                if self._retryable_status(response.status_code) and attempt + 1 < self._config.retry_attempts:
                    await asyncio.sleep(self._config.retry_backoff_seconds * (2**attempt))
                    continue
                try:
                    raise_for_problem(response)
                except APIError as exc:
                    if not self._retryable_status(response.status_code) or attempt + 1 >= self._config.retry_attempts:
                        raise
                    last_error = exc
                    await asyncio.sleep(self._config.retry_backoff_seconds * (2**attempt))
                    continue
                return response
            except httpx.TransportError as exc:
                last_error = exc
            await asyncio.sleep(self._config.retry_backoff_seconds * (2**attempt))
        if last_error is not None:
            raise last_error
        msg = "Request failed without a response."
        raise RuntimeError(msg)

    def _parse(self, response: httpx.Response, model: type[BaseModel]) -> Any:
        return model.model_validate(response.json())

    async def health(self) -> HealthResponse:
        response = await self._request("GET", "health")
        return self._parse(response, HealthResponse)

    async def version(self) -> VersionResponse:
        response = await self._request("GET", "version")
        return self._parse(response, VersionResponse)

    async def embed(self, texts: Iterable[str]) -> EmbedResponse:
        request = EmbedRequest(texts=list(texts))
        response = await self._request("POST", "embed", json=self._model_payload(request))
        return self._parse(response, EmbedResponse)

    async def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        db_path: str = "./lancedb_data",
    ) -> SearchResponse:
        request = SearchRequest(query=query, top_k=top_k, db_path=db_path)
        response = await self._request("POST", "search", json=self._model_payload(request))
        return self._parse(response, SearchResponse)

    async def process(
        self,
        input_text: str,
        *,
        source: str = "legislation",
        generate_embeddings: bool = False,
    ) -> ProcessResponse:
        request = ProcessRequest(
            input=input_text,
            source=source,
            generate_embeddings=generate_embeddings,
        )
        response = await self._request("POST", "process", json=self._model_payload(request))
        return self._parse(response, ProcessResponse)


__all__ = ["AsyncNLPPolicyNZClient"]
