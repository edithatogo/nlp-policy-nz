"""Structured logging and request-scoped observability helpers."""

from __future__ import annotations

import contextvars
import json
import logging
import os
import sys
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "nlp_policy_nz_request_id",
    default=None,
)


def current_request_id() -> str | None:
    """Return the active request id, if one is set."""
    return request_id_var.get()


def set_request_id(request_id: str | None) -> contextvars.Token[str | None]:
    """Set the active request id for the current context."""
    return request_id_var.set(request_id)


def reset_request_id(token: contextvars.Token[str | None]) -> None:
    """Reset the active request id using a token returned from set_request_id."""
    request_id_var.reset(token)


def generate_request_id() -> str:
    """Generate a stable request identifier."""
    import uuid

    return uuid.uuid4().hex


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def config_hash(payload: dict[str, Any]) -> str:
    """Return a deterministic config hash for startup diagnostics."""
    serialized = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")
    return sha256(serialized).hexdigest()[:16]


class JsonFormatter(logging.Formatter):
    """Render log records as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        """Render the log record as a compact JSON string."""
        payload: dict[str, Any] = {
            "timestamp": _utc_now(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", current_request_id()),
        }
        for field in (
            "endpoint",
            "duration_ms",
            "duration_seconds",
            "method",
            "status",
            "version",
            "config_hash",
            "error_code",
            "scope",
            "client_ip",
            "degraded",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def get_structured_logger(name: str) -> logging.Logger:
    """Return a logger that emits JSON records to stderr."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
    logger.propagate = False
    if not any(isinstance(handler.formatter, JsonFormatter) for handler in logger.handlers):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger
