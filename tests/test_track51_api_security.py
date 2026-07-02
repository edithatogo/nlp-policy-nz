"""Track 51 API security and authentication contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nlp_policy_nz.api import server
from nlp_policy_nz.api.auth import (
    APIKeyStore,
    SecuritySettings,
    build_audit_logger,
    required_scope_for_path,
)
from nlp_policy_nz.cli.main import main
from nlp_policy_nz.config import FeatureFlags, RuntimeSettings


def test_track51_auth_helpers_cover_scopes_and_headers() -> None:
    """Helper functions should resolve API-key headers and endpoint scopes."""
    assert required_scope_for_path("/health") is None
    assert required_scope_for_path("/v2/embed") == "read"
    assert required_scope_for_path("/v2/search") == "read"
    assert required_scope_for_path("/v2/process") == "write"
    assert required_scope_for_path("/auth/create-key") == "admin"


def test_track51_key_store_lifecycle_round_trip(tmp_path: Path) -> None:
    """The hashed key store should support create, authenticate, revoke, and rotate."""
    store_path = tmp_path / "config" / "api_keys.json"
    store = APIKeyStore.load(store_path)

    secret, record = store.create_key(name="service", scopes=["read", "write"])
    assert secret.startswith("npnz_")
    assert record.key_hash not in secret
    assert store_path.is_file()
    assert secret not in store_path.read_text(encoding="utf-8")

    authenticated = APIKeyStore.load(store_path).authenticate(secret, "read")
    assert authenticated.key_id == record.key_id

    revoked = store.revoke_key(record.key_id)
    assert revoked.revoked is True

    rotated_secret, old_record, new_record = store.rotate_key(record.key_id)
    assert rotated_secret.startswith("npnz_")
    assert old_record.revoked is True
    assert new_record.key_id != old_record.key_id


def test_track51_cli_auth_commands_manage_keys(tmp_path: Path, monkeypatch, capsys) -> None:
    """CLI auth commands should write and mutate the key store deterministically."""
    monkeypatch.chdir(tmp_path)

    main(["auth", "create-key", "--name", "service", "--scopes", "read", "write"])
    created = json.loads(capsys.readouterr().out)
    key_id = created["record"]["key_id"]
    secret = created["secret_key"]
    assert secret.startswith("npnz_")

    main(["auth", "list-keys"])
    listed = json.loads(capsys.readouterr().out)
    assert listed[0]["key_id"] == key_id

    main(["auth", "revoke-key", "--key-id", key_id])
    revoked = json.loads(capsys.readouterr().out)
    assert revoked["revoked"] is True

    main(["auth", "list-keys"])
    relisted = json.loads(capsys.readouterr().out)
    assert relisted[0]["revoked"] is True


def test_track51_server_authentication_scope_and_audit_logging(tmp_path: Path, monkeypatch) -> None:
    """The API should enforce auth, scope checks, security headers, and audit logs."""
    store_path = tmp_path / "config" / "api_keys.json"
    audit_log_path = tmp_path / "logs" / "api_audit.log"
    store = APIKeyStore.load(store_path)
    read_secret, _ = store.create_key(name="reader", scopes=["read"])
    write_secret, _ = store.create_key(name="writer", scopes=["write"])

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
        RuntimeSettings(rate_limit_per_minute=2, cors_origins=("https://example.test",)),
    )
    monkeypatch.setattr(
        server,
        "_feature_flags",
        FeatureFlags(enable_v1=True, enable_v2=True, embed_enabled=True, search_enabled=True, process_enabled=True),
    )
    server._rate_limit_history.clear()

    class DummyResult:
        dimension = 2

        def __init__(self, embedding: list[float]) -> None:
            self.embedding = embedding

    class DummyGenerator:
        model_name = "dummy-model"

        def embed_batch(self, texts):  # noqa: ANN001
            return [DummyResult([1.0, 2.0]) for _ in texts]

    async def fake_inline_pipeline(request, t0):  # noqa: ANN001
        return server.ProcessResponse(
            records=[{"doc_id": "doc-1"}],
            source=request.source,
            count=1,
            output_path=None,
            elapsed_seconds=0.01,
        )

    def fake_generator() -> DummyGenerator:
        return DummyGenerator()

    def fake_search(**kwargs):  # noqa: ANN001
        return [{"doc_id": "doc-1", "text": "match"}]

    monkeypatch.setattr(server, "_get_embedding_generator", fake_generator)
    monkeypatch.setattr(server, "search_similar", fake_search)
    monkeypatch.setattr(server, "_run_inline_pipeline", fake_inline_pipeline)

    client = TestClient(server.app)

    health = client.get("/health")
    assert health.status_code == 200

    unauthenticated = client.post("/v2/embed", json={"texts": ["hello"]})
    assert unauthenticated.status_code == 401

    read_embed = client.post(
        "/v2/embed",
        json={"texts": ["hello"]},
        headers={"Authorization": f"Bearer {read_secret}"},
    )
    assert read_embed.status_code == 200
    assert read_embed.headers["x-content-type-options"] == "nosniff"
    assert read_embed.headers["x-ratelimit-limit"] == "2"
    assert read_embed.json()["model_name"] == "dummy-model"

    wrong_scope = client.post(
        "/v2/process",
        json={"input": "inline text", "source": "legislation", "generate_embeddings": False},
        headers={"Authorization": f"Bearer {read_secret}"},
    )
    assert wrong_scope.status_code == 403

    write_process = client.post(
        "/v2/process",
        json={"input": "inline text", "source": "legislation", "generate_embeddings": False},
        headers={"Authorization": f"Bearer {write_secret}"},
    )
    assert write_process.status_code == 200
    assert write_process.headers["x-ratelimit-remaining"] in {"0", "1"}

    audit_entries = [json.loads(line) for line in audit_log_path.read_text(encoding="utf-8").splitlines()]
    assert any(entry["endpoint"] == "/v2/embed" and entry["status"] == 401 for entry in audit_entries)
    assert any(entry["endpoint"] == "/v2/embed" and entry["key_hash"] for entry in audit_entries)
    assert any(entry["endpoint"] == "/v2/process" and entry["status"] == 403 for entry in audit_entries)
    assert any(entry["client_ip"] for entry in audit_entries)
