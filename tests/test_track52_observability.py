"""Track 52 observability and error-standardization contract tests."""

from __future__ import annotations

import io
import json
import logging
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from nlp_policy_nz.api import server
from nlp_policy_nz.api.auth import APIKeyStore, SecuritySettings, build_audit_logger
from nlp_policy_nz.client import APIError, ErrorCode, NLPPolicyNZClient
from nlp_policy_nz.config import FeatureFlags, RuntimeSettings


def _configure_server(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    degraded_embeddings: bool = False,
) -> str:
    store_path = tmp_path / "config" / "api_keys.json"
    audit_log_path = tmp_path / "logs" / "api_audit.log"
    store = APIKeyStore.load(store_path)
    secret, _ = store.create_key(name="reader", scopes=["read", "write", "admin"])

    monkeypatch.setattr(
        server,
        "_security_settings",
        SecuritySettings(
            auth_required=True,
            api_keys_path=store_path,
            audit_log_path=audit_log_path,
            max_body_bytes=1024,
        ),
    )
    monkeypatch.setattr(server, "_api_key_store", APIKeyStore.load(store_path))
    monkeypatch.setattr(server, "_audit_logger", build_audit_logger(audit_log_path))
    monkeypatch.setattr(
        server,
        "_settings",
        RuntimeSettings(rate_limit_per_minute=5, cors_origins=("https://example.test",)),
    )
    monkeypatch.setattr(
        server,
        "_feature_flags",
        FeatureFlags(
            enable_v1=True,
            enable_v2=True,
            embed_enabled=True,
            search_enabled=True,
            process_enabled=True,
            degraded_embeddings=degraded_embeddings,
        ),
    )
    monkeypatch.setattr(server, "_embedding_load_failed", degraded_embeddings)
    server._rate_limit_history.clear()
    return secret


def test_track52_request_ids_logs_and_problem_details(tmp_path: Path, monkeypatch) -> None:
    """Responses should include request IDs and RFC 7807 payloads on auth errors."""
    secret = _configure_server(tmp_path, monkeypatch)
    client = TestClient(server.app)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(server.logger.handlers[0].formatter)
    server.logger.addHandler(handler)

    try:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.headers["x-request-id"]

        denied = client.post("/v2/embed", json={"texts": ["hello"]})
        assert denied.status_code == 401
        assert denied.headers["content-type"].startswith("application/problem+json")
        body = denied.json()
        assert body["code"] == "AUTH_INVALID_KEY"
        assert body["request_id"] == denied.headers["x-request-id"]

        auth_embed = client.post(
            "/v2/embed",
            json={"texts": []},
            headers={"Authorization": f"Bearer {secret}"},
        )
        assert auth_embed.status_code == 422
        assert auth_embed.headers["content-type"].startswith("application/problem+json")
        assert auth_embed.json()["code"] == "VALIDATION_ERROR"
        assert auth_embed.json()["errors"]

        parsed = [json.loads(line) for line in stream.getvalue().splitlines() if line.strip()]
        assert {entry["endpoint"] for entry in parsed} >= {"/health", "/v2/embed"}
        assert all(entry["request_id"] for entry in parsed)
        assert any(entry["message"] == "request complete" for entry in parsed)
    finally:
        server.logger.removeHandler(handler)


def test_track52_metrics_and_degraded_fallback(tmp_path: Path, monkeypatch) -> None:
    """Metrics should expose Prometheus text and degraded search should stay available."""
    secret = _configure_server(tmp_path, monkeypatch, degraded_embeddings=True)
    client = TestClient(server.app)

    degraded = client.post(
        "/v2/search",
        json={"query": "climate adaptation", "top_k": 2},
        headers={"Authorization": f"Bearer {secret}"},
    )
    assert degraded.status_code == 200
    assert degraded.headers["x-degraded"] == "true"
    assert degraded.json()["results"]

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "nlp_policy_nz_requests_total" in metrics.text
    assert "nlp_policy_nz_active_requests" in metrics.text
    assert "nlp_policy_nz_model_loaded" in metrics.text

    embed = client.post(
        "/v2/embed",
        json={"texts": ["hello"]},
        headers={"Authorization": f"Bearer {secret}"},
    )
    assert embed.status_code == 503
    assert embed.headers["content-type"].startswith("application/problem+json")
    assert embed.json()["code"] == "MODEL_NOT_LOADED"


def test_track52_client_sdk_parses_problem_details() -> None:
    """The client SDK should surface RFC 7807 payloads as typed API errors."""
    def handler(request: httpx.Request) -> httpx.Response:
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

    client = NLPPolicyNZClient(
        base_url="https://example.test",
        api_key="secret",
        transport=httpx.MockTransport(handler),
        retry_attempts=1,
    )

    with pytest.raises(APIError) as exc_info:
        client.embed(["hello"])

    assert exc_info.value.code == ErrorCode.AUTH_INSUFFICIENT_SCOPE
    assert exc_info.value.problem is not None
    assert exc_info.value.problem.request_id == "req-1"


def test_track52_openapi_includes_problem_detail_schema() -> None:
    """OpenAPI should advertise problem-detail response schemas."""
    schema = server.app.openapi()

    assert "ProblemDetail" in schema["components"]["schemas"]
    assert "ProblemError" in schema["components"]["schemas"]
    embed_responses = schema["paths"]["/v2/embed"]["post"]["responses"]
    assert "401" in embed_responses
    assert "application/problem+json" in embed_responses["401"]["content"]
