"""Explicit archive schema migration entry points."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from nlp_policy_nz.archive.schema import ArchiveBundle

CURRENT_SCHEMA_VERSION = "1.0.0"


def migrate_bundle(
    payload: Mapping[str, Any], *, target_version: str = CURRENT_SCHEMA_VERSION
) -> ArchiveBundle:
    """Migrate supported pre-release payloads to the current schema."""
    if target_version != CURRENT_SCHEMA_VERSION:
        raise ValueError(f"unsupported target schema version: {target_version}")
    source_version = str(payload.get("schema_version", ""))
    if source_version not in {"0.9.0", CURRENT_SCHEMA_VERSION}:
        raise ValueError(f"unsupported source schema version: {source_version}")
    migrated = dict(payload)
    migrated["schema_version"] = CURRENT_SCHEMA_VERSION
    return ArchiveBundle.model_validate(migrated)


__all__ = ["CURRENT_SCHEMA_VERSION", "migrate_bundle"]
