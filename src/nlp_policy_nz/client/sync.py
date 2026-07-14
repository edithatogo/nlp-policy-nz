"""Synchronous API client for nlp-policy-nz."""

# ruff: noqa: ANN401, D102, D105, PLR0911, TRY300, PYI034

from __future__ import annotations

import time
import types
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

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

RetrySleep = Callable[[float], None]


@dataclass(slots=True)
class _ClientConfig:
    base_url: str
    api_prefix: str
    timeout: float
    retry_attempts: int
    retry_backoff_seconds: float
    api_key: str | None
    api_key_header: str
    api_key_prefix: str


class _BaseClient:
    """Common request helpers shared by sync and async clients."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8000",
        api_prefix: str = "v1",
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_backoff_seconds: float = 0.25,
        api_key: str | None = None,
        api_key_header: str = "X-API-Key",
        api_key_prefix: str = "",
    ) -> None:
        self._config = _ClientConfig(
            base_url=base_url.rstrip("/"),
            api_prefix=api_prefix.strip("/"),
            timeout=timeout,
            retry_attempts=max(1, retry_attempts),
            retry_backoff_seconds=max(0.0, retry_backoff_seconds),
            api_key=api_key,
            api_key_header=api_key_header,
            api_key_prefix=api_key_prefix,
        )

    def _url(self, path: str) -> str:
        return urljoin(
            f"{self._config.base_url}/",
            f"{self._config.api_prefix}/{path.lstrip('/')}",
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._config.api_key:
            token = self._config.api_key
            if self._config.api_key_prefix:
                token = f"{self._config.api_key_prefix} {token}"
            headers[self._config.api_key_header] = token
        return headers

    @staticmethod
    def _retryable_status(status_code: int) -> bool:
        return status_code in {500, 502, 503, 504}

    @staticmethod
    def _model_payload(model: BaseModel | dict[str, Any]) -> dict[str, Any]:
        if isinstance(model, BaseModel):
            return model.model_dump(mode="json")
        return model


class NLPPolicyNZClient(_BaseClient):
    """Synchronous client for the public API."""

    def __init__(self, **kwargs: Any) -> None:
        transport = kwargs.pop("transport", None)
        super().__init__(**kwargs)
        self._client = httpx.Client(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            headers=self._headers(),
            transport=transport,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> NLPPolicyNZClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: types.TracebackType | None,
    ) -> None:
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        sleep_fn: RetrySleep = time.sleep,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(self._config.retry_attempts):
            try:
                response = self._client.request(
                    method,
                    self._url(path),
                    json=json,
                    headers=self._headers(),
                )
                if self._retryable_status(response.status_code) and attempt + 1 < self._config.retry_attempts:
                    sleep_fn(self._config.retry_backoff_seconds * (2**attempt))
                    continue
                try:
                    raise_for_problem(response)
                except APIError as exc:
                    if not self._retryable_status(response.status_code) or attempt + 1 >= self._config.retry_attempts:
                        raise
                    last_error = exc
                    sleep_fn(self._config.retry_backoff_seconds * (2**attempt))
                    continue
                return response
            except httpx.TransportError as exc:
                last_error = exc
            sleep_fn(self._config.retry_backoff_seconds * (2**attempt))
        if last_error is not None:
            raise last_error
        msg = "Request failed without a response."
        raise RuntimeError(msg)

    def _parse(self, response: httpx.Response, model: type[BaseModel]) -> Any:
        return model.model_validate(response.json())

    def health(self) -> HealthResponse:
        response = self._request("GET", "health")
        return self._parse(response, HealthResponse)

    def version(self) -> VersionResponse:
        response = self._request("GET", "version")
        return self._parse(response, VersionResponse)

    def embed(self, texts: Iterable[str]) -> EmbedResponse:
        request = EmbedRequest(texts=list(texts))
        response = self._request("POST", "embed", json=self._model_payload(request))
        return self._parse(response, EmbedResponse)

    def search(self, query: str, *, top_k: int = 5, db_path: str = "./lancedb_data") -> SearchResponse:
        request = SearchRequest(query=query, top_k=top_k, db_path=db_path)
        response = self._request("POST", "search", json=self._model_payload(request))
        return self._parse(response, SearchResponse)

    def process(
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
        response = self._request("POST", "process", json=self._model_payload(request))
        return self._parse(response, ProcessResponse)


__all__ = ["NLPPolicyNZClient"]
