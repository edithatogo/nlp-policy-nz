"""Track 83 API surface, OpenAPI, and SDK contract tests."""

from __future__ import annotations

import asyncio
import copy
import inspect
from typing import Any

import httpx
from fastapi.testclient import TestClient

from nlp_policy_nz.api import API_CONTRACT_VERSION, API_VERSIONS, AUTH_SCOPE_MAP, ENDPOINT_INVENTORY
from nlp_policy_nz.api.server import app
from nlp_policy_nz.client import APIError, AsyncNLPPolicyNZClient, ErrorCode, NLPPolicyNZClient


def _openapi_contract_view(schema: dict[str, Any]) -> dict[str, Any]:
    """Strip version-specific markers so the contract can be compared directly."""
    view = copy.deepcopy(schema)
    view.pop("x-api-version", None)
    return view


def _expected_aliases(path: str, versions: tuple[str, ...]) -> list[str]:
    """Mirror the alias expansion used by the API contract metadata."""
    aliases = [path]
    if path.startswith(("/v1/", "/v2/")):
        return aliases
    for version in versions:
        if version in API_VERSIONS:
            aliases.append(f"/{version}{path}")
    return aliases


def test_track83_openapi_surface_is_versioned_and_stable() -> None:
    """The public OpenAPI document should remain stable across versioned views."""
    app.openapi_schema = None
    canonical = app.openapi()
    client = TestClient(app)
    v1 = client.get("/v1/openapi.json").json()
    v2 = client.get("/v2/openapi.json").json()

    assert canonical["x-api-contract-version"] == API_CONTRACT_VERSION
    assert canonical["x-api-versions"] == list(API_VERSIONS)
    assert canonical["x-api-version"] == "canonical"
    assert _openapi_contract_view(canonical) == _openapi_contract_view(v1)
    assert _openapi_contract_view(canonical) == _openapi_contract_view(v2)
    assert canonical["x-endpoint-inventory"] == [
        {
            "method": item.method,
            "path": item.path,
            "aliases": _expected_aliases(item.path, item.versions),
            "operation_id": item.operation_id,
            "summary": item.summary,
            "tag": item.tag,
            "request_model": item.request_model,
            "response_model": item.response_model,
            "scope": item.scope,
            "versions": list(item.versions),
            "error_codes": list(item.error_codes),
            "deprecated": item.deprecated,
        }
        for item in ENDPOINT_INVENTORY
    ]
    assert canonical["x-auth-scope-map"] == AUTH_SCOPE_MAP
    assert canonical["x-path-scope-map"]["/v1/embed"] == "read"
    assert canonical["x-path-scope-map"]["/v2/process"] == "write"

    paths = canonical["paths"]
    assert {"/health", "/v1/health", "/v2/health", "/embed", "/v1/embed", "/v2/embed"} <= set(paths)
    operation_ids = [
        operation["operationId"]
        for path_item in paths.values()
        for operation in path_item.values()
        if isinstance(operation, dict) and "operationId" in operation
    ]
    assert len(operation_ids) == len(set(operation_ids))
    assert "ProblemDetail" in canonical["components"]["schemas"]
    assert "ProblemError" in canonical["components"]["schemas"]
    assert "ApiKeyAuth" in canonical["components"]["securitySchemes"]


def test_track83_problem_detail_round_trip() -> None:
    """The server should emit RFC 7807 payloads for validation failures."""
    client = TestClient(app)
    response = client.post("/v2/embed", json={"texts": []})

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["instance"] == "/v2/embed"
    assert body["errors"]
    assert response.headers["x-request-id"] == body["request_id"]


def test_track83_sync_and_async_sdk_parity() -> None:
    """The sync and async clients should expose the same public API and route shapes."""
    public_sync_methods = {
        name
        for name, value in inspect.getmembers(NLPPolicyNZClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }
    public_async_methods = {
        name
        for name, value in inspect.getmembers(AsyncNLPPolicyNZClient, predicate=inspect.isfunction)
        if not name.startswith("_")
    }

    assert public_sync_methods >= {"health", "version", "embed", "search", "process"}
    assert public_sync_methods >= {"close"}
    assert public_async_methods >= {"health", "version", "embed", "search", "process"}
    assert public_async_methods >= {"aclose"}

    sync_signatures = {
        name: str(inspect.signature(getattr(NLPPolicyNZClient, name)))
        for name in ("health", "version", "embed", "search", "process")
    }
    async_signatures = {
        name: str(inspect.signature(getattr(AsyncNLPPolicyNZClient, name)))
        for name in ("health", "version", "embed", "search", "process")
    }
    assert sync_signatures == async_signatures

    sync_calls: list[tuple[str, str]] = []
    async_calls: list[tuple[str, str]] = []

    def sync_handler(request: httpx.Request) -> httpx.Response:
        sync_calls.append((request.method, request.url.path))
        return _sdk_response(request.url.path)

    async def async_handler(request: httpx.Request) -> httpx.Response:
        async_calls.append((request.method, request.url.path))
        return _sdk_response(request.url.path)

    sync_client = NLPPolicyNZClient(
        base_url="https://example.test",
        transport=httpx.MockTransport(sync_handler),
        retry_attempts=1,
    )
    async_client = AsyncNLPPolicyNZClient(
        base_url="https://example.test",
        transport=httpx.MockTransport(async_handler),
        retry_attempts=1,
    )

    try:
        assert sync_client.health().status == "ok"
        assert sync_client.version().version == "0.1.0"
        assert sync_client.embed(["hello"]).count == 1
        assert sync_client.search("climate", top_k=1).count == 1
        assert sync_client.process("text").count == 1

        async def run_async_calls() -> None:
            assert (await async_client.health()).status == "ok"
            assert (await async_client.version()).version == "0.1.0"
            assert (await async_client.embed(["hello"])).count == 1
            assert (await async_client.search("climate", top_k=1)).count == 1
            assert (await async_client.process("text")).count == 1

        asyncio.run(run_async_calls())
    finally:
        sync_client.close()
        asyncio.run(async_client.aclose())

    assert sync_calls == async_calls
    assert sync_calls == [
        ("GET", "/v1/health"),
        ("GET", "/v1/version"),
        ("POST", "/v1/embed"),
        ("POST", "/v1/search"),
        ("POST", "/v1/process"),
    ]


def _sdk_response(path: str) -> httpx.Response:
    if path.endswith("/health"):
        return httpx.Response(
            200,
            json={
                "status": "ok",
                "pipeline_status": "ok",
                "db_connected": True,
                "model_loaded": False,
                "model_name": "",
                "version": "0.1.0",
                "last_run_timestamp": None,
            },
        )
    if path.endswith("/version"):
        return httpx.Response(
            200,
            json={
                "version": "0.1.0",
                "build_timestamp": "2026-07-02T00:00:00Z",
                "commit_sha": "unknown",
                "dataset_revision": "0",
            },
        )
    if path.endswith("/embed"):
        return httpx.Response(
            200,
            json={
                "embeddings": [[0.1, 0.2]],
                "model_name": "dummy",
                "dimension": 2,
                "count": 1,
                "elapsed_seconds": 0.01,
            },
        )
    if path.endswith("/search"):
        return httpx.Response(
            200,
            json={
                "results": [{"doc_id": "doc-1", "text": "matched", "corpus_source": "legislation"}],
                "query": "climate",
                "count": 1,
                "elapsed_seconds": 0.01,
            },
        )
    if path.endswith("/process"):
        return httpx.Response(
            200,
            json={
                "records": [{"doc_id": "doc-1"}],
                "source": "legislation",
                "count": 1,
                "output_path": None,
                "elapsed_seconds": 0.01,
            },
        )
    return httpx.Response(404, json={"detail": "unexpected path"})


def test_track83_sdk_problem_parsing_is_typed() -> None:
    """Both SDKs should parse RFC 7807 responses into typed API errors."""

    def sync_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/embed"
        return httpx.Response(
            403,
            headers={"content-type": "application/problem+json"},
            json={
                "type": "https://nlp-policy-nz.local/problems/auth_insufficient_scope",
                "title": "Forbidden",
                "status": 403,
                "detail": "API key does not have write scope.",
                "instance": "/v1/embed",
                "code": "AUTH_INSUFFICIENT_SCOPE",
                "errors": None,
                "request_id": "req-1",
            },
        )

    async def async_handler(request: httpx.Request) -> httpx.Response:
        return sync_handler(request)

    sync_client = NLPPolicyNZClient(
        base_url="https://example.test",
        api_key="secret",
        transport=httpx.MockTransport(sync_handler),
        retry_attempts=1,
    )
    async_client = AsyncNLPPolicyNZClient(
        base_url="https://example.test",
        api_key="secret",
        transport=httpx.MockTransport(async_handler),
        retry_attempts=1,
    )

    try:
        try:
            sync_client.embed(["hello"])
            raise AssertionError("sync client did not raise")
        except APIError as exc:
            assert exc.code == ErrorCode.AUTH_INSUFFICIENT_SCOPE
            assert exc.problem is not None
            assert exc.problem.request_id == "req-1"

        async def run_async_error() -> None:
            try:
                await async_client.embed(["hello"])
                raise AssertionError("async client did not raise")
            except APIError as exc:
                assert exc.code == ErrorCode.AUTH_INSUFFICIENT_SCOPE
                assert exc.problem is not None
                assert exc.problem.request_id == "req-1"

        asyncio.run(run_async_error())
    finally:
        sync_client.close()
        asyncio.run(async_client.aclose())
