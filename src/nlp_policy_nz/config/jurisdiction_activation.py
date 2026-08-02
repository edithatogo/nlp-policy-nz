"""Externally pinned activation authority for jurisdiction profiles."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field, model_validator

from nlp_policy_nz.config.jurisdiction_contracts import (
    ProfileLoadError,
    read_unique_document,
    validate_json_schema,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class ProfileActivationGrant(BaseModel):
    """One exact capability authorization bound to an approved profile."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    profile_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    capability: Literal["route_records", "extract_assertions", "export_ontology"]
    authorization_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authorized_at: str


class ProfileActivationRegistry(BaseModel):
    """Immutable activation grants whose digest must be supplied externally."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0.0"]
    registry_id: Literal["jurisdiction-profile-activations"]
    registry_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    registry_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    grants: tuple[ProfileActivationGrant, ...]

    @model_validator(mode="after")
    def _reject_duplicate_grants(self) -> ProfileActivationRegistry:
        keys = [
            (
                grant.profile_id,
                grant.profile_version,
                grant.profile_sha256,
                grant.capability,
            )
            for grant in self.grants
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("activation grants must be unique")
        return self

    def authorizes(
        self,
        *,
        profile_id: str,
        profile_version: str,
        profile_sha256: str,
        capability: str,
    ) -> bool:
        """Return whether one exact profile capability has an external grant."""
        return any(
            grant.profile_id == profile_id
            and grant.profile_version == profile_version
            and grant.profile_sha256 == profile_sha256
            and grant.capability == capability
            for grant in self.grants
        )


def canonical_activation_registry_digest(
    registry: Mapping[str, Any] | ProfileActivationRegistry,
) -> str:
    """Hash canonical registry content while excluding its self-pin."""
    if isinstance(registry, ProfileActivationRegistry):
        payload = registry.model_dump(mode="json")
    else:
        payload = dict(registry)
    payload.pop("registry_sha256", None)
    return sha256(orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)).hexdigest()


def load_profile_activation_registry(
    path: str | Path,
    *,
    expected_registry_sha256: str,
) -> ProfileActivationRegistry:
    """Load a registry only when its self-pin and external pin both match."""
    if len(expected_registry_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in expected_registry_sha256
    ):
        raise ProfileLoadError("activation registry external pin must be a SHA-256 digest")
    registry_path = Path(path)
    payload = read_unique_document(registry_path)
    validate_json_schema(payload, "jurisdiction_activation_registry.schema.json")
    try:
        registry = ProfileActivationRegistry.model_validate(payload)
    except ValueError as error:
        raise ProfileLoadError(f"invalid activation registry: {registry_path}") from error
    actual_digest = canonical_activation_registry_digest(payload)
    if registry.registry_sha256 != actual_digest:
        raise ProfileLoadError("activation registry self-pin does not match canonical content")
    if registry.registry_sha256 != expected_registry_sha256:
        raise ProfileLoadError("activation registry does not match its external pin")
    return registry
