"""Forward-only migration that adds ``schema_version`` to pipeline records."""

from __future__ import annotations


def upgrade(payload: dict[str, object]) -> dict[str, object]:
    """Add the canonical schema version to a payload."""
    upgraded = dict(payload)
    upgraded.setdefault("schema_version", "1.1")
    return upgraded


def downgrade(payload: dict[str, object]) -> dict[str, object]:
    """Remove the schema version marker."""
    downgraded = dict(payload)
    downgraded.pop("schema_version", None)
    return downgraded
