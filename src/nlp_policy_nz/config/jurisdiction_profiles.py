"""Strict, hash-pinned jurisdiction profile loading and fail-closed routing."""

from __future__ import annotations

import re
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from nlp_policy_nz.config.jurisdiction_activation import (
    ProfileActivationRegistry,
    load_profile_activation_registry,
)
from nlp_policy_nz.config.jurisdiction_contracts import (
    ProfileLoadError,
    read_unique_document,
    validate_json_schema,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class ProfileStatus(StrEnum):
    """Activation state declared by a jurisdiction profile."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    UNSUPPORTED = "unsupported"


class CapabilityStatus(StrEnum):
    """Closed support states for profile capabilities."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    UNSUPPORTED = "unsupported"


class ProfileCapability(StrEnum):
    """Capabilities governed by the initial profile contract."""

    ROUTE_RECORDS = "route_records"
    EXTRACT_ASSERTIONS = "extract_assertions"
    EXPORT_ONTOLOGY = "export_ontology"


class CorpusProfile(BaseModel):
    """Corpus identity constraints supplied by one jurisdiction profile."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    default_id: str = Field(pattern=r"^corpus-[a-z0-9]+(?:-[a-z0-9]+)*$")
    id_pattern: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_default_matches_pattern(self) -> CorpusProfile:
        try:
            pattern = re.compile(self.id_pattern)
        except re.error as error:
            raise ValueError("corpus.id_pattern must be a valid regular expression") from error
        if pattern.fullmatch(self.default_id) is None:
            raise ValueError("corpus.default_id must match corpus.id_pattern")
        return self


class OntologyPin(BaseModel):
    """Exact ontology identity for an enabled profile."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ontology_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    ontology_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    ontology_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class JurisdictionProfile(BaseModel):
    """Versioned jurisdiction configuration with no permissive fallback."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0.0"]
    profile_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    profile_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    status: ProfileStatus
    country: str = Field(pattern=r"^[A-Z]{2}$")
    jurisdiction_id: str = Field(pattern=r"^[A-Z]{2}(?:-[A-Z0-9]+)+$")
    jurisdiction_name: str = Field(min_length=1)
    corpus: CorpusProfile
    capabilities: dict[ProfileCapability, CapabilityStatus]
    ontology_pin: OntologyPin | None
    blockers: tuple[str, ...] = ()

    @field_validator("capabilities")
    @classmethod
    def _require_complete_capability_set(
        cls,
        value: dict[ProfileCapability, CapabilityStatus],
    ) -> dict[ProfileCapability, CapabilityStatus]:
        expected = set(ProfileCapability)
        if set(value) != expected:
            missing = sorted(item.value for item in expected - set(value))
            raise ValueError(f"capabilities must declare the closed set; missing={missing}")
        return value

    @field_validator("blockers")
    @classmethod
    def _reject_blank_blockers(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item.strip() for item in value):
            raise ValueError("blockers must be non-empty strings")
        return value

    @model_validator(mode="after")
    def _validate_activation_boundaries(self) -> JurisdictionProfile:
        enabled_capabilities = [
            capability
            for capability, status in self.capabilities.items()
            if status is CapabilityStatus.ENABLED
        ]
        if self.status is ProfileStatus.ENABLED:
            if not enabled_capabilities:
                raise ValueError("enabled profiles must enable at least one capability")
            if self.ontology_pin is None:
                raise ValueError("enabled profiles require an ontology pin")
        else:
            if enabled_capabilities:
                raise ValueError("inactive profiles cannot enable capabilities")
            if not self.blockers:
                raise ValueError("inactive profiles must declare blockers")
        return self


class ProfileResolution(BaseModel):
    """Deterministic routing result that makes abstention explicit."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["routed", "abstained"]
    reason: str = Field(min_length=1)
    profile: JurisdictionProfile | None = None


class ProfileRegistry:
    """Immutable profile registry with exact identity resolution."""

    def __init__(
        self,
        profiles: tuple[JurisdictionProfile, ...],
        *,
        activation_registry: ProfileActivationRegistry | None = None,
    ) -> None:
        indexed: dict[tuple[str, str], JurisdictionProfile] = {}
        for profile in profiles:
            key = (profile.profile_id, profile.profile_version)
            if key in indexed:
                raise ProfileLoadError(
                    f"duplicate profile/version: {profile.profile_id}@{profile.profile_version}"
                )
            indexed[key] = profile
        for profile in profiles:
            for capability, status in profile.capabilities.items():
                if status is not CapabilityStatus.ENABLED:
                    continue
                if activation_registry is None:
                    raise ProfileLoadError(
                        "enabled profiles require an externally pinned activation registry"
                    )
                if not activation_registry.authorizes(
                    profile_id=profile.profile_id,
                    profile_version=profile.profile_version,
                    profile_sha256=profile.profile_sha256,
                    capability=capability.value,
                ):
                    raise ProfileLoadError(
                        "enabled profile capability lacks an exact activation grant"
                    )
        self._profiles = tuple(
            sorted(profiles, key=lambda item: (item.profile_id, item.profile_version))
        )
        self._indexed = indexed

    @property
    def profiles(self) -> tuple[JurisdictionProfile, ...]:
        """Return profiles in deterministic identity order."""
        return self._profiles

    def resolve(  # noqa: PLR0911
        self,
        profile_id: str,
        *,
        version: str,
        profile_sha256: str,
        capability: str,
    ) -> ProfileResolution:
        """Resolve an exact active profile or abstain without a default."""
        matches = [profile for profile in self._profiles if profile.profile_id == profile_id]
        if not matches:
            return ProfileResolution(status="abstained", reason="unknown profile_id")
        profile = self._indexed.get((profile_id, version))
        if profile is None:
            return ProfileResolution(status="abstained", reason="unknown profile version")
        if profile.profile_sha256 != profile_sha256:
            return ProfileResolution(status="abstained", reason="profile pin mismatch")
        if profile.status is not ProfileStatus.ENABLED:
            return ProfileResolution(status="abstained", reason="profile is not enabled")
        try:
            parsed_capability = ProfileCapability(capability)
        except ValueError:
            return ProfileResolution(status="abstained", reason="unknown capability")
        if profile.capabilities[parsed_capability] is not CapabilityStatus.ENABLED:
            return ProfileResolution(status="abstained", reason="capability is not enabled")
        return ProfileResolution(status="routed", reason="exact active profile", profile=profile)


def canonical_profile_digest(profile: Mapping[str, Any] | JurisdictionProfile) -> str:
    """Hash canonical profile content while excluding its self-pin."""
    if isinstance(profile, JurisdictionProfile):
        payload = profile.model_dump(mode="json")
    else:
        payload = dict(profile)
    payload.pop("profile_sha256", None)
    rendered = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)
    return sha256(rendered).hexdigest()


def load_jurisdiction_profile(
    path: str | Path,
    *,
    expected_profile_id: str | None = None,
    expected_version: str | None = None,
    expected_sha256: str | None = None,
) -> JurisdictionProfile:
    """Load one profile and bind all caller-supplied identity expectations."""
    profile_path = Path(path)
    payload = read_unique_document(profile_path)
    validate_json_schema(payload, "jurisdiction_profile.schema.json")
    try:
        profile = JurisdictionProfile.model_validate(payload)
    except ValueError as error:
        raise ProfileLoadError(f"invalid jurisdiction profile: {profile_path}") from error
    actual_digest = canonical_profile_digest(payload)
    if profile.profile_sha256 != actual_digest:
        raise ProfileLoadError("profile self-pin does not match canonical content")
    if expected_profile_id is not None and profile.profile_id != expected_profile_id:
        raise ProfileLoadError("profile_id does not match expected identity")
    if expected_version is not None and profile.profile_version != expected_version:
        raise ProfileLoadError("profile version does not match expected identity")
    if expected_sha256 is not None and profile.profile_sha256 != expected_sha256:
        raise ProfileLoadError("profile digest does not match expected pin")
    return profile


def load_jurisdiction_profiles(
    directory: str | Path,
    *,
    activation_registry_path: str | Path | None = None,
    expected_activation_registry_sha256: str | None = None,
) -> ProfileRegistry:
    """Load every JSON/YAML profile in one directory into a strict registry."""
    profile_directory = Path(directory)
    if not profile_directory.is_dir():
        raise ProfileLoadError(f"profile directory does not exist: {profile_directory}")
    paths = sorted(
        path
        for path in profile_directory.iterdir()
        if path.is_file() and path.suffix in {".json", ".yaml", ".yml"}
    )
    if not paths:
        raise ProfileLoadError("profile directory contains no supported profile documents")
    if (activation_registry_path is None) != (expected_activation_registry_sha256 is None):
        raise ProfileLoadError(
            "activation registry path and external pin must be supplied together"
        )
    activation_registry = (
        load_profile_activation_registry(
            activation_registry_path,
            expected_registry_sha256=expected_activation_registry_sha256,
        )
        if activation_registry_path is not None and expected_activation_registry_sha256 is not None
        else None
    )
    return ProfileRegistry(
        tuple(load_jurisdiction_profile(path) for path in paths),
        activation_registry=activation_registry,
    )
