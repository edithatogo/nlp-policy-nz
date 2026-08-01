"""Versioned, fail-closed jurisdiction profile loading."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ProfileError(ValueError):
    """Raised when a jurisdiction profile is unknown or invalid."""


@dataclass(frozen=True)
class JurisdictionProfile:
    """Validated jurisdiction routing metadata."""

    profile_id: str
    country: str
    corpus_id_prefix: str
    adapter: str
    version: str
    digest: str


class ProfileLoader:
    """Load only known, digest-verified jurisdiction profiles."""

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = directory or Path(__file__).resolve().parents[2] / "config" / "jurisdictions"

    def load(self, profile_id: str) -> JurisdictionProfile:
        """Load a profile, raising instead of falling back to NZ."""
        if not profile_id or any(part in profile_id for part in ("/", "\\", "..")):
            raise ProfileError(f"invalid jurisdiction profile_id: {profile_id!r}")
        path = self.directory / f"{profile_id}.json"
        if not path.is_file():
            raise ProfileError(f"unknown jurisdiction profile_id: {profile_id!r}")
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProfileError(f"cannot read jurisdiction profile: {profile_id!r}") from exc
        self._validate(raw, profile_id)
        return JurisdictionProfile(**{key: raw[key] for key in JurisdictionProfile.__dataclass_fields__})

    @staticmethod
    def _validate(raw: dict[str, Any], profile_id: str) -> None:
        required = {"profile_id", "country", "corpus_id_prefix", "adapter", "version", "digest"}
        if set(raw) != required or raw["profile_id"] != profile_id:
            raise ProfileError(f"invalid fields in jurisdiction profile: {profile_id!r}")
        if raw["version"] != "1.0.0" or not all(isinstance(raw[key], str) and raw[key] for key in required):
            raise ProfileError(f"invalid version or value in jurisdiction profile: {profile_id!r}")
        unsigned = {key: raw[key] for key in required if key != "digest"}
        expected = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if raw["digest"] != f"sha256:{expected}":
            raise ProfileError(f"digest mismatch in jurisdiction profile: {profile_id!r}")
