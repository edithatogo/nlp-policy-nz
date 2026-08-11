"""Tests for API key authentication, authorization, and audit logging helpers."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from nlp_policy_nz.api.auth import (
    APIKeyRecord,
    APIKeyStore,
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


def test_normalize_scopes():
    assert _normalize_scopes([" READ ", "write", "READ"]) == ("read", "write")
    assert _normalize_scopes([]) == ()


def test_hash_key():
    secret = "my_" + "secret_key"
    hashed = _hash_key(secret)
    assert isinstance(hashed, str)
    assert len(hashed) == 64  # SHA-256


def test_load_security_settings(monkeypatch):
    monkeypatch.setenv("NLP_POLICY_NZ_REQUIRE_API_AUTH", "true")
    monkeypatch.setenv("NLP_POLICY_NZ_API_KEYS_PATH", "config//keys.json")

    settings = load_security_settings()
    assert settings.auth_required is True
    assert settings.api_keys_path == Path("config//keys.json")


def test_api_key_record_serialization():
    data = {
        "key_id": "test_id",
        "name": "Test Key",
        "key_hash": "hash123",
        "scopes": ["read", "write"],
        "created_at": "2023-01-01T00:00:00Z",
    }
    record = APIKeyRecord.from_dict(data)
    assert record.key_id == "test_id"
    assert record.name == "Test Key"
    assert record.key_hash == "hash123"
    assert record.scopes == ("read", "write")

    serialized = record.to_dict()
    assert serialized["key_id"] == "test_id"
    assert serialized["scopes"] == ["read", "write"]
    assert serialized["revoked"] is False


def test_api_key_record_is_expired():
    # No expiration
    record = APIKeyRecord(
        key_id="test_id", name="Test", key_hash="hash", scopes=("read",), created_at=_utc_now()
    )
    assert record.is_expired() is False

    # Expired
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    record.expires_at = past
    assert record.is_expired() is True

    # Future expiration
    future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    record.expires_at = future
    assert record.is_expired() is False


def test_api_key_record_allows():
    record = APIKeyRecord(
        key_id="test", name="Test", key_hash="hash", scopes=("read", "write"), created_at=_utc_now()
    )
    assert record.allows("read") is True
    assert record.allows("WRITE") is True
    assert record.allows("admin") is False

    admin_record = APIKeyRecord(
        key_id="admin", name="Admin", key_hash="hash", scopes=("admin",), created_at=_utc_now()
    )
    assert admin_record.allows("read") is True
    assert admin_record.allows("admin") is True


def test_api_key_store(tmp_path):
    store_path = tmp_path / "keys.json"
    store = APIKeyStore(path=store_path)

    # Create key
    secret, record = store.create_key(name="App1", scopes=["read"])
    assert record.key_id is not None
    assert secret.startswith("npnz_")

    # Load store from path
    store2 = APIKeyStore.load(store_path)
    assert len(store2.records) == 1
    assert store2.records[0].key_id == record.key_id

    # Authenticate
    context = store.authenticate(secret, "read")
    assert context.name == "App1"
    assert context.scopes == ("read",)

    # Invalid scope
    with pytest.raises(PermissionError, match="API key does not have write scope"):
        store.authenticate(secret, "write")

    # Invalid secret
    with pytest.raises(PermissionError, match="Invalid API key"):
        store.authenticate("invalid", "read")


def test_api_key_store_revoke(tmp_path):
    store = APIKeyStore(path=tmp_path / "keys.json")
    secret, record = store.create_key(name="App1", scopes=["read"])

    store.revoke_key(record.key_id)
    with pytest.raises(PermissionError, match="Invalid API key"):
        store.authenticate(secret, "read")


def test_api_key_store_rotate(tmp_path):
    store = APIKeyStore(path=tmp_path / "keys.json")
    secret, record = store.create_key(name="App1", scopes=["read"])

    new_secret, old_record, new_record = store.rotate_key(record.key_id)
    assert old_record.revoked is True
    assert new_record.revoked is False

    with pytest.raises(PermissionError, match="Invalid API key"):
        store.authenticate(secret, "read")

    context = store.authenticate(new_secret, "read")
    assert context.key_id == new_record.key_id


def test_required_scope_for_path():
    assert required_scope_for_path("/health") is None
    assert required_scope_for_path("/v1/search") == "read"
    assert required_scope_for_path("/v1/process") == "write"
    assert required_scope_for_path("/auth/keys") == "admin"
    assert required_scope_for_path("/unknown") is None


def test_extract_api_key():
    assert extract_api_key({"Authorization": "Bearer token123"}) == "token123"
    assert extract_api_key({"X-API-Key": "token456"}) == "token456"
    assert extract_api_key({}) is None
    assert extract_api_key({"Authorization": "Basic something"}) is None


def test_audit_logger(tmp_path):
    log_path = tmp_path / "audit.log"
    logger = build_audit_logger(log_path)

    emit_audit_event(logger, {"event": "test", "status": "ok"})

    content = log_path.read_text()
    assert '"event": "test"' in content
    assert '"status": "ok"' in content


def test_verify_api_key(tmp_path):
    store = APIKeyStore(path=tmp_path / "keys.json")
    secret, record = store.create_key(name="App", scopes=["write"])
    context = verify_api_key(store, secret, "write")
    assert context.key_id == record.key_id


def test_api_key_store_list_and_get(tmp_path):
    store = APIKeyStore(path=tmp_path / "keys.json")
    _, record1 = store.create_key(name="App1", scopes=["read"])
    _, record2 = store.create_key(name="App2", scopes=["write"])

    # Test list_keys
    keys = store.list_keys()
    assert len(keys) == 2
    assert keys[0].key_id == record1.key_id
    assert keys[1].key_id == record2.key_id

    # Test get (found)
    fetched = store.get(record1.key_id)
    assert fetched is not None
    assert fetched.key_id == record1.key_id

    # Test get (not found)
    assert store.get("nonexistent") is None


def test_api_key_store_errors(tmp_path):
    store = APIKeyStore(path=tmp_path / "keys.json")

    with pytest.raises(KeyError, match="Unknown key_id"):
        store.revoke_key("nonexistent")

    with pytest.raises(KeyError, match="Unknown key_id"):
        store.rotate_key("nonexistent")


def test_load_security_settings_defaults(monkeypatch):
    monkeypatch.delenv("NLP_POLICY_NZ_REQUIRE_API_AUTH", raising=False)
    monkeypatch.delenv("NLP_POLICY_NZ_API_KEYS_PATH", raising=False)
    monkeypatch.delenv("NLP_POLICY_NZ_API_AUDIT_LOG_PATH", raising=False)
    monkeypatch.delenv("NLP_POLICY_NZ_MAX_BODY_BYTES", raising=False)

    settings = load_security_settings()
    assert settings.auth_required is False
    assert settings.api_keys_path == Path("config/api_keys.json")
    assert settings.audit_log_path == Path("logs/api_audit.log")
    assert settings.max_body_bytes == 1048576


def test_api_key_store_load_missing_file(tmp_path):
    store_path = tmp_path / "nonexistent.json"
    store = APIKeyStore.load(store_path)
    assert len(store.records) == 0


def test_api_key_store_save_creates_dir(tmp_path):
    nested_path = tmp_path / "nested" / "dir" / "keys.json"
    store = APIKeyStore(path=nested_path)
    store.create_key(name="test", scopes=["read"])
    assert nested_path.is_file()
