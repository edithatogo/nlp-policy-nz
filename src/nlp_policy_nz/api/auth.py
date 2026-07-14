"""API key authentication, authorization, and audit logging helpers."""

# ruff: noqa: D102

from __future__ import annotations

import json
import logging
import secrets
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_scopes(scopes: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({scope.strip().lower() for scope in scopes if scope.strip()}))


def _hash_key(secret: str) -> str:
    return sha256(secret.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class SecuritySettings:
    """Runtime security settings for API key auth and audit logging."""

    auth_required: bool = False
    api_keys_path: Path = Path("config/api_keys.json")
    audit_log_path: Path = Path("logs/api_audit.log")
    max_body_bytes: int = 1_048_576


def load_security_settings() -> SecuritySettings:
    """Load security settings from environment variables."""
    import os

    return SecuritySettings(
        auth_required=os.getenv("NLP_POLICY_NZ_REQUIRE_API_AUTH", "false").strip().lower()
        in {"1", "true", "yes", "on"},
        api_keys_path=Path(os.getenv("NLP_POLICY_NZ_API_KEYS_PATH", "config/api_keys.json")),
        audit_log_path=Path(os.getenv("NLP_POLICY_NZ_API_AUDIT_LOG_PATH", "logs/api_audit.log")),
        max_body_bytes=int(os.getenv("NLP_POLICY_NZ_MAX_BODY_BYTES", "1048576")),
    )


@dataclass(slots=True)
class APIKeyRecord:
    """Stored metadata for a hashed API key."""

    key_id: str
    name: str
    key_hash: str
    scopes: tuple[str, ...]
    created_at: str
    expires_at: str | None = None
    last_used: str | None = None
    revoked: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> APIKeyRecord:
        return cls(
            key_id=str(data["key_id"]),
            name=str(data["name"]),
            key_hash=str(data["key_hash"]),
            scopes=tuple(str(scope) for scope in data.get("scopes", [])),
            created_at=str(data["created_at"]),
            expires_at=data.get("expires_at"),
            last_used=data.get("last_used"),
            revoked=bool(data.get("revoked", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "name": self.name,
            "key_hash": self.key_hash,
            "scopes": list(self.scopes),
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used": self.last_used,
            "revoked": self.revoked,
        }

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.fromisoformat(self.expires_at) <= datetime.now(UTC)

    def allows(self, scope: str) -> bool:
        normalized_scope = scope.lower()
        return "admin" in self.scopes or normalized_scope in self.scopes


@dataclass(slots=True)
class AuthContext:
    """Authenticated request context."""

    key_id: str
    key_hash: str
    name: str
    scopes: tuple[str, ...]


def verify_api_key(store: APIKeyStore, secret: str, required_scope: str) -> AuthContext:
    """Validate an API key against the store and required scope."""
    return store.authenticate(secret, required_scope)


@dataclass(slots=True)
class APIKeyStore:
    """JSON-backed key store for API authentication."""

    path: Path
    records: list[APIKeyRecord] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path) -> APIKeyStore:
        path = Path(path)
        if not path.is_file():
            return cls(path=path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = [APIKeyRecord.from_dict(item) for item in payload.get("keys", [])]
        return cls(path=path, records=records)

    def save(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "keys": [record.to_dict() for record in self.records]}
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return self.path

    def list_keys(self) -> list[APIKeyRecord]:
        return sorted(self.records, key=lambda record: record.created_at)

    def get(self, key_id: str) -> APIKeyRecord | None:
        for record in self.records:
            if record.key_id == key_id:
                return record
        return None

    def _next_key_id(self) -> str:
        return secrets.token_hex(8)

    def create_key(
        self,
        *,
        name: str,
        scopes: Iterable[str],
        expires_at: str | None = None,
    ) -> tuple[str, APIKeyRecord]:
        key_id = self._next_key_id()
        secret = f"npnz_{key_id}_{secrets.token_urlsafe(24)}"
        record = APIKeyRecord(
            key_id=key_id,
            name=name,
            key_hash=_hash_key(secret),
            scopes=_normalize_scopes(scopes),
            created_at=_utc_now(),
            expires_at=expires_at,
        )
        self.records.append(record)
        self.save()
        return secret, record

    def revoke_key(self, key_id: str) -> APIKeyRecord:
        record = self.get(key_id)
        if record is None:
            msg = f"Unknown key_id: {key_id}"
            raise KeyError(msg)
        record.revoked = True
        self.save()
        return record

    def rotate_key(
        self,
        key_id: str,
    ) -> tuple[str, APIKeyRecord, APIKeyRecord]:
        record = self.get(key_id)
        if record is None:
            msg = f"Unknown key_id: {key_id}"
            raise KeyError(msg)
        old_record = APIKeyRecord(
            key_id=record.key_id,
            name=record.name,
            key_hash=record.key_hash,
            scopes=record.scopes,
            created_at=record.created_at,
            expires_at=record.expires_at,
            last_used=record.last_used,
            revoked=True,
        )
        record.revoked = True
        secret, new_record = self.create_key(
            name=record.name,
            scopes=record.scopes,
            expires_at=record.expires_at,
        )
        self.save()
        return secret, old_record, new_record

    def authenticate(self, secret: str, required_scope: str) -> AuthContext:
        key_hash = _hash_key(secret)
        record = next(
            (
                candidate
                for candidate in self.records
                if candidate.key_hash == key_hash and not candidate.revoked and not candidate.is_expired()
            ),
            None,
        )
        if record is None:
            msg = "Invalid API key."
            raise PermissionError(msg)
        if not record.allows(required_scope):
            msg = f"API key does not have {required_scope} scope."
            raise PermissionError(msg)
        record.last_used = _utc_now()
        self.save()
        return AuthContext(
            key_id=record.key_id,
            key_hash=record.key_hash,
            name=record.name,
            scopes=record.scopes,
        )


def required_scope_for_path(path: str) -> str | None:
    """Return the required scope for a request path, if any."""
    normalized = path.rstrip("/")
    if normalized in {
        "/health",
        "/version",
        "/v1/health",
        "/v2/health",
        "/v1/version",
        "/v2/version",
        "/openapi.json",
        "/docs",
        "/redoc",
    }:
        return None
    if normalized.endswith(("/embed", "/search")):
        return "read"
    if normalized.endswith("/process"):
        return "write"
    if normalized.startswith("/auth"):
        return "admin"
    return None


def extract_api_key(headers: dict[str, str]) -> str | None:
    """Extract an API key from Authorization or X-API-Key headers."""
    authorization = headers.get("authorization") or headers.get("Authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip() or None
    api_key = headers.get("x-api-key") or headers.get("X-API-Key")
    return api_key.strip() if api_key else None


def build_audit_logger(log_path: str | Path) -> logging.Logger:
    """Return a logger that appends JSON audit events to a rotating log."""
    logger_name = f"nlp_policy_nz.api.audit.{Path(log_path).resolve()}"
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger


def emit_audit_event(logger: logging.Logger, payload: dict[str, Any]) -> None:
    """Write a structured audit event."""
    logger.info(json.dumps(payload, sort_keys=True, ensure_ascii=False))


__all__ = [
    "APIKeyRecord",
    "APIKeyStore",
    "AuthContext",
    "SecuritySettings",
    "build_audit_logger",
    "emit_audit_event",
    "extract_api_key",
    "load_security_settings",
    "required_scope_for_path",
    "verify_api_key",
]
