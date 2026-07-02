"""CLI helpers for API key lifecycle management."""

# ruff: noqa: D103

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from nlp_policy_nz.api.auth import APIKeyStore


def _store(path: str | Path | None) -> APIKeyStore:
    store_path = Path(path) if path is not None else Path("config/api_keys.json")
    return APIKeyStore.load(store_path)


def create_api_key(
    *,
    name: str,
    scopes: Iterable[str],
    expires_at: str | None = None,
    store_path: str | Path | None = None,
) -> dict[str, Any]:
    store = _store(store_path)
    secret, record = store.create_key(name=name, scopes=scopes, expires_at=expires_at)
    return {"secret_key": secret, "record": record.to_dict(), "store_path": str(store.path)}


def list_api_keys(*, store_path: str | Path | None = None) -> list[dict[str, Any]]:
    store = _store(store_path)
    return [record.to_dict() for record in store.list_keys()]


def revoke_api_key(*, key_id: str, store_path: str | Path | None = None) -> dict[str, Any]:
    store = _store(store_path)
    record = store.revoke_key(key_id)
    return record.to_dict()


def rotate_api_key(*, key_id: str, store_path: str | Path | None = None) -> dict[str, Any]:
    store = _store(store_path)
    secret, old_record, new_record = store.rotate_key(key_id)
    return {
        "secret_key": secret,
        "revoked": old_record.to_dict(),
        "record": new_record.to_dict(),
        "store_path": str(store.path),
    }


__all__ = [
    "create_api_key",
    "list_api_keys",
    "revoke_api_key",
    "rotate_api_key",
]
