import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from nlp_policy_nz.api.auth import (
    APIKeyRecord,
    APIKeyStore,
    SecuritySettings,
    _hash_key,
    _normalize_scopes,
    _utc_now,
    build_audit_logger,
    emit_audit_event,
    extract_api_key,
    load_security_settings,
    required_scope_for_path,
    verify_api_key,
)


def test_utc_now():
    now_str = _utc_now()
    assert now_str.endswith("Z")
    # Should be parseable back to datetime
    dt = datetime.fromisoformat(now_str.replace("Z", "+00:00"))
    assert dt.tzinfo is not None


def test_normalize_scopes():
    assert _normalize_scopes(["  read  ", "WRITE", "read", ""]) == ("read", "write")
    assert _normalize_scopes([]) == ()


def test_hash_key():
    secret = "my_secret"
    hash1 = _hash_key(secret)
    hash2 = _hash_key(secret)
    assert hash1 == hash2
    assert _hash_key("other") != hash1
    assert len(hash1) == 64


def test_load_security_settings(monkeypatch):
    monkeypatch.setenv("NLP_POLICY_NZ_REQUIRE_API_AUTH", "yes")
    monkeypatch.setenv("NLP_POLICY_NZ_API_KEYS_PATH", "/tmp/keys.json")
    monkeypatch.setenv("NLP_POLICY_NZ_API_AUDIT_LOG_PATH", "/tmp/audit.log")
    monkeypatch.setenv("NLP_POLICY_NZ_MAX_BODY_BYTES", "2048")

    settings = load_security_settings()
    assert settings.auth_required is True
    assert settings.api_keys_path == Path("/tmp/keys.json")
    assert settings.audit_log_path == Path("/tmp/audit.log")
    assert settings.max_body_bytes == 2048


def test_api_key_record_serialization():
    data = {
        "key_id": "test_id",
        "name": "Test Key",
        "key_hash": "hash123",
        "scopes": ["read", "write"],
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2025-01-01T00:00:00Z",
        "last_used": None,
        "revoked": False,
    }
    record = APIKeyRecord.from_dict(data)
    assert record.key_id == "test_id"
    assert record.scopes == ("read", "write")

    out_data = record.to_dict()
    assert out_data["scopes"] == ["read", "write"]
    assert out_data["created_at"] == "2024-01-01T00:00:00Z"


def test_api_key_record_is_expired():
    record = APIKeyRecord(
        key_id="1", name="a", key_hash="h", scopes=(), created_at=_utc_now()
    )
    assert not record.is_expired()

    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    record.expires_at = past
    assert record.is_expired()

    future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    record.expires_at = future
    assert not record.is_expired()


def test_api_key_record_allows():
    record = APIKeyRecord(
        key_id="1", name="a", key_hash="h", scopes=("read",), created_at=_utc_now()
    )
    assert record.allows("read")
    assert record.allows("READ")
    assert not record.allows("write")

    admin_record = APIKeyRecord(
        key_id="2", name="a", key_hash="h", scopes=("admin",), created_at=_utc_now()
    )
    assert admin_record.allows("read")
    assert admin_record.allows("write")


def test_api_key_store_lifecycle(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore.load(store_path)
    assert not store.records

    secret, record = store.create_key(name="test", scopes=["read"])
    assert record.key_id
    assert record.key_hash == _hash_key(secret)
    assert record.scopes == ("read",)

    # Save and reload
    store2 = APIKeyStore.load(store_path)
    assert len(store2.records) == 1
    assert store2.records[0].key_id == record.key_id

    # Authenticate success
    auth_ctx = store.authenticate(secret, "read")
    assert auth_ctx.key_id == record.key_id
    assert auth_ctx.name == "test"

    # Authenticate failure - scope
    with pytest.raises(PermissionError, match="does not have write scope"):
        store.authenticate(secret, "write")

    # Authenticate failure - invalid secret
    with pytest.raises(PermissionError, match="Invalid API key"):
        store.authenticate("wrong", "read")

    # Revoke key
    store.revoke_key(record.key_id)
    with pytest.raises(PermissionError, match="Invalid API key"):
        store.authenticate(secret, "read")


def test_api_key_store_rotate_key(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)

    secret, record = store.create_key(name="rotate_me", scopes=["read"])

    new_secret, old_record, new_record = store.rotate_key(record.key_id)
    assert old_record.revoked is True
    assert new_record.revoked is False
    assert new_record.name == "rotate_me"

    # Old secret fails
    with pytest.raises(PermissionError):
        store.authenticate(secret, "read")

    # New secret works
    auth_ctx = store.authenticate(new_secret, "read")
    assert auth_ctx.key_id == new_record.key_id


def test_required_scope_for_path():
    assert required_scope_for_path("/health") is None
    assert required_scope_for_path("/v1/version/") is None

    assert required_scope_for_path("/api/v1/search") == "read"
    assert required_scope_for_path("/data/embed") == "read"

    assert required_scope_for_path("/jobs/process") == "write"

    assert required_scope_for_path("/auth/keys") == "admin"

    assert required_scope_for_path("/unknown") is None


def test_extract_api_key():
    assert extract_api_key({"authorization": "Bearer secret123"}) == "secret123"
    assert extract_api_key({"Authorization": "Bearer secret123"}) == "secret123"

    assert extract_api_key({"x-api-key": "key456"}) == "key456"
    assert extract_api_key({"X-API-Key": "key456"}) == "key456"

    assert extract_api_key({"other": "value"}) is None
    assert extract_api_key({"authorization": "Basic xyz"}) is None


def test_audit_logger(tmp_path):
    log_file = tmp_path / "audit.log"
    logger = build_audit_logger(log_file)

    emit_audit_event(logger, {"event": "test", "user": "admin"})

    # Verify log content
    content = log_file.read_text(encoding="utf-8")
    assert '"event": "test"' in content
    assert '"user": "admin"' in content


def test_verify_api_key(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)
    secret, _ = store.create_key(name="test", scopes=["read"])

    auth_ctx = verify_api_key(store, secret, "read")
    assert auth_ctx.name == "test"


def test_api_key_store_list_keys(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)

    store.create_key(name="test1", scopes=["read"])
    store.create_key(name="test2", scopes=["read"])

    keys = store.list_keys()
    assert len(keys) == 2
    assert keys[0].name == "test1"
    assert keys[1].name == "test2"


def test_api_key_store_get(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)

    _, record = store.create_key(name="test1", scopes=["read"])

    found = store.get(record.key_id)
    assert found is not None
    assert found.name == "test1"

    assert store.get("unknown_id") is None


def test_api_key_store_revoke_key_not_found(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)

    with pytest.raises(KeyError, match="Unknown key_id"):
        store.revoke_key("unknown_id")


def test_api_key_store_rotate_key_not_found(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)

    with pytest.raises(KeyError, match="Unknown key_id"):
        store.rotate_key("unknown_id")
