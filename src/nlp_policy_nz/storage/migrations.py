"""Forward-only migration registry for pipeline record schemas."""

from __future__ import annotations

from collections.abc import Callable

MIGRATION_REGISTRY: dict[str, dict[str, str]] = {
    "1.0": {"from": "legacy", "to": "1.0", "description": "Initial schema"},
    "1.1": {
        "from": "1.0",
        "to": "1.1",
        "description": "Add schema_version field for production hardening",
    },
}


def current_schema_version() -> str:
    """Return the current canonical pipeline schema version."""
    return "1.1"


def apply_migration(
    payload: dict[str, object],
    migration: Callable[[dict[str, object]], dict[str, object]],
) -> dict[str, object]:
    """Apply a migration function to a record payload."""
    return migration(dict(payload))


def add_schema_version(payload: dict[str, object]) -> dict[str, object]:
    """Upgrade an old payload with the canonical schema version."""
    upgraded = dict(payload)
    upgraded.setdefault("schema_version", current_schema_version())
    return upgraded


def strip_schema_version(payload: dict[str, object]) -> dict[str, object]:
    """Downgrade a payload by removing schema version metadata."""
    downgraded = dict(payload)
    downgraded.pop("schema_version", None)
    return downgraded
