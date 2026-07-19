"""Fail-closed ingestion contracts for the HathiTrust-NZ archive.

The module models metadata and work planning only. It deliberately does not
download source content, which keeps corpus acquisition in the cloud workflow
that owns the relevant credentials and publication gates.
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AccessClass(StrEnum):
    """Access boundary used by Hathi-NZ publication routing."""

    PUBLIC_METADATA = "public_metadata"
    PUBLIC_FULL_TEXT = "public_full_text"
    PUBLIC_DERIVED_FEATURES = "public_derived_features"
    RESTRICTED_METADATA = "restricted_metadata"
    RESTRICTED_DERIVED = "restricted_derived"


class PublicationDecision(StrEnum):
    """Maximum content publication decision for one source item."""

    METADATA_ONLY = "metadata_only"
    PUBLIC_FULL_TEXT = "public_full_text"


class RightsBasis(StrEnum):
    """Controlled basis for a reviewable rights assertion."""

    HATHI_RIGHTS_PROFILE = "hathitrust_rights_profile"
    PUBLIC_DOMAIN = "public_domain"
    OPEN_LICENSE = "open_license"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class AcquisitionMode(StrEnum):
    """Permitted source acquisition route."""

    API = "api"
    GITHUB_ACTIONS = "github_actions"
    STATIC_HOST = "static_host"
    INTERNET_ARCHIVE = "internet_archive"
    PREPARED_BUNDLE = "prepared_bundle"


class HathiRightsEvidence(BaseModel):
    """Immutable provenance and purpose permissions for a rights assertion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rights_basis: RightsBasis
    authoritative_record_uri: str = Field(min_length=1, pattern=r"^https?://")
    authoritative_snapshot_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    accessed_at: datetime
    territorial_applicability: tuple[str, ...] = Field(min_length=1)
    may_acquire: bool = False
    may_process: bool = False
    may_publish_full_text: bool = False
    may_publish_derived_features: bool = False

    @field_validator("accessed_at")
    @classmethod
    def _require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("accessed_at must include a timezone")
        return value

    @field_validator("territorial_applicability")
    @classmethod
    def _require_nonempty_territories(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        territories = tuple(item.strip().upper() for item in value)
        if not territories or any(not item for item in territories):
            raise ValueError("territorial_applicability must contain non-empty territories")
        return territories

    def permits(self, purpose: str, *, territory: str = "NZ") -> bool:
        """Return whether this evidence affirmatively permits a purpose in territory."""
        if self.rights_basis is RightsBasis.UNKNOWN:
            return False
        if territory.upper() not in self.territorial_applicability:
            return False
        permissions = {
            "acquire": self.may_acquire,
            "process": self.may_process,
            "publish_full_text": self.may_publish_full_text,
            "publish_derived_features": self.may_publish_derived_features,
        }
        return permissions.get(purpose, False)


class HathiDatasetDescriptor(BaseModel):
    """A publication dataset registered in the Hathi-NZ collection."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9-]+$")
    access_class: AccessClass
    hf_repo: str = Field(min_length=1)
    role: str | None = None


class HathiArchiveRegistry(BaseModel):
    """Validated collection-level registry summary and dataset descriptors."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    registry_version: str = Field(min_length=1)
    collection_id: str = Field(min_length=1)
    source_collection_id: str = Field(min_length=1)
    curated_seed_record_count: int = Field(ge=0)
    datasets: tuple[HathiDatasetDescriptor, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_unique_datasets(self) -> Self:
        dataset_ids = [dataset.dataset_id for dataset in self.datasets]
        if len(dataset_ids) != len(set(dataset_ids)):
            raise ValueError("duplicate dataset id")
        return self

    @property
    def dataset_ids(self) -> tuple[str, ...]:
        """Return dataset identifiers in deterministic order."""
        return tuple(dataset.dataset_id for dataset in self.datasets)

    @classmethod
    def from_items(
        cls,
        items: tuple[HathiArchiveItem, ...],
        *,
        registry_version: str = "1.0",
        collection_id: str = "hathitrust-nz",
        source_collection_id: str = "unknown",
        curated_seed_record_count: int = 0,
    ) -> Self:
        """Build a registry projection from item rows and reject duplicates."""
        identities = [(item.dataset_id, item.item_id) for item in items]
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate item identity")
        descriptors = tuple(
            HathiDatasetDescriptor(
                dataset_id=dataset_id,
                access_class=access_class,
                hf_repo=f"unknown/{dataset_id}",
            )
            for dataset_id, access_class in sorted(
                {(item.dataset_id, item.access_class) for item in items},
                key=lambda value: value[0],
            )
        )
        return cls(
            registry_version=registry_version,
            collection_id=collection_id,
            source_collection_id=source_collection_id,
            curated_seed_record_count=curated_seed_record_count,
            datasets=descriptors,
        )


class HathiArchiveItem(BaseModel):
    """One source item with rights, provenance, and publication routing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    _restricted_profiles: ClassVar[tuple[str, ...]] = (
        "pdus",
        "ic",
        "ic-world",
        "und",
        "supp",
        "google-restricted",
        "privacy",
        "page-only",
    )

    collection_id: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9-]+$")
    source_id: str = Field(min_length=1)
    item_id: str = Field(min_length=1)
    htid: str = Field(min_length=1)
    access_class: AccessClass
    acquisition_mode: AcquisitionMode = AcquisitionMode.GITHUB_ACTIONS
    source_url: str = Field(min_length=1)
    source_dataset_name: str = Field(min_length=1)
    rights_code: str | None = None
    rights_evidence: HathiRightsEvidence | None = None
    digitization_profile: str = Field(min_length=1)
    publish_eligibility: PublicationDecision
    source_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    expected_record_count: int | None = Field(default=None, ge=0)
    notes: str = ""

    @field_validator("htid")
    @classmethod
    def _validate_htid(cls, value: str) -> str:
        if "/" in value or any(char.isspace() for char in value):
            raise ValueError("htid must be a normalized, whitespace-free identifier")
        return value

    @model_validator(mode="after")
    def _validate_content_contract(self) -> Self:
        if self.publish_eligibility is PublicationDecision.PUBLIC_FULL_TEXT:
            if self.access_class is not AccessClass.PUBLIC_FULL_TEXT:
                raise ValueError("public full-text publication requires public_full_text access")
            if self.source_sha256 is None:
                raise ValueError("source_sha256 is required for public full-text publication")
            if self.rights_evidence is None:
                raise ValueError("rights evidence is required for public full-text publication")
            required_purposes = ("acquire", "process", "publish_full_text")
            if not all(self.rights_evidence.permits(purpose) for purpose in required_purposes):
                raise ValueError(
                    "affirmative NZ rights evidence is required for public full-text publication"
                )
        return self

    @property
    def content_allowed(self) -> bool:
        """Return whether full text may enter a public work package."""
        profile = self.digitization_profile.casefold()
        restricted = {part for part in profile.replace("_", "-").split("-") if part}
        return (
            self.publish_eligibility is PublicationDecision.PUBLIC_FULL_TEXT
            and self.access_class is AccessClass.PUBLIC_FULL_TEXT
            and self.source_sha256 is not None
            and self.rights_evidence is not None
            and all(
                self.rights_evidence.permits(purpose)
                for purpose in ("acquire", "process", "publish_full_text")
            )
            and not any(
                token in profile or token in restricted
                for token in self._restricted_profiles
                if len(token) > 2 or token in restricted
            )
        )

    def publication_decision(self) -> PublicationDecision:
        """Apply the fail-closed rights gate to the declared decision."""
        return (
            PublicationDecision.PUBLIC_FULL_TEXT
            if self.content_allowed
            else PublicationDecision.METADATA_ONLY
        )

    @property
    def derived_features_allowed(self) -> bool:
        """Return whether derived features may be published in New Zealand."""
        return self.rights_evidence is not None and all(
            self.rights_evidence.permits(purpose)
            for purpose in ("acquire", "process", "publish_derived_features")
        )

    @property
    def content_address(self) -> str:
        """Return a stable address for content or metadata-only work."""
        if self.source_sha256 is not None:
            return f"sha256:{self.source_sha256}"
        identity = f"{self.collection_id}|{self.dataset_id}|{self.item_id}|{self.source_url}"
        return f"identity:{sha256(identity.encode('utf-8')).hexdigest()}"


class HathiWorkItem(BaseModel):
    """Cloud work item derived from a validated archive item."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    htid: str
    dataset_id: str
    source_id: str
    source_url: str
    content_address: str
    publication_decision: PublicationDecision
    content_allowed: bool
    acquisition_mode: AcquisitionMode
    rights_evidence: HathiRightsEvidence | None = None
    derived_features_allowed: bool = False


class HathiWorkShard(BaseModel):
    """Deterministic shard of cloud work item identities."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    shard_id: str
    item_ids: tuple[str, ...]


class HathiWorkManifest(BaseModel):
    """Resumable work plan that contains metadata, not corpus payloads."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1.0"
    producer: str = "nlp-policy-nz"
    pipeline_version: str = Field(min_length=1)
    collection_id: str = Field(min_length=1)
    items: tuple[HathiWorkItem, ...]
    shards: tuple[HathiWorkShard, ...]


HATHI_CAPABILITY_REGISTRY: tuple[dict[str, Any], ...] = (
    {
        "capability_id": "hathi.registry.validate",
        "summary": "Validate HathiTrust-NZ registry and rights routing.",
        "side_effect": "read_only",
        "surfaces": {
            "cli": "not_implemented",
            "api": "not_implemented",
            "sdk": "not_implemented",
            "mcp": "not_implemented",
        },
    },
    {
        "capability_id": "hathi.work.plan",
        "summary": "Build deterministic, content-addressed cloud work shards.",
        "side_effect": "read_only",
        "surfaces": {
            "cli": "not_implemented",
            "api": "not_implemented",
            "sdk": "not_implemented",
            "mcp": "not_implemented",
        },
    },
)

_ACCESS_CLASS_ALIASES: dict[str, AccessClass] = {
    "public_full_text_where_confirmed": AccessClass.PUBLIC_FULL_TEXT,
    "public_derived_features": AccessClass.PUBLIC_DERIVED_FEATURES,
    "public_scripts_aggregates_and_reproducibility_metadata": AccessClass.PUBLIC_DERIVED_FEATURES,
    "metadata_only_until_static_host_bundle_is_eligible": AccessClass.RESTRICTED_METADATA,
    "public_metadata": AccessClass.PUBLIC_METADATA,
}


def load_archive_registry(path: str | Path) -> HathiArchiveRegistry:
    """Load the Hathi-NZ registry projection without acquiring corpus data."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    collection = payload.get("collection")
    if not isinstance(collection, dict):
        raise ValueError("archive registry collection is required")
    raw_datasets = payload.get("datasets")
    if not isinstance(raw_datasets, list):
        raise ValueError("archive registry datasets must be a list")
    datasets = tuple(
        HathiDatasetDescriptor(
            dataset_id=str(dataset["dataset_id"]),
            access_class=_normalise_access_class(str(dataset["access_class"])),
            hf_repo=str(dataset.get("hf_repo", "unknown/unknown")),
            role=str(dataset["role"]) if dataset.get("role") is not None else None,
        )
        for dataset in raw_datasets
    )
    return HathiArchiveRegistry(
        registry_version=str(payload.get("registry_version", "1.0")),
        collection_id=str(collection["collection_id"]),
        source_collection_id=str(collection["source_collection_id"]),
        curated_seed_record_count=int(collection["curated_seed_record_count"]),
        datasets=datasets,
    )


def hathi_capability_registry() -> tuple[dict[str, Any], ...]:
    """Return planned read-only CLI/API/SDK/MCP capability metadata."""
    return tuple(dict(capability) for capability in HATHI_CAPABILITY_REGISTRY)


def _normalise_access_class(value: str) -> AccessClass:
    """Map registry labels to the finite contract vocabulary."""
    if value in _ACCESS_CLASS_ALIASES:
        return _ACCESS_CLASS_ALIASES[value]
    try:
        return AccessClass(value)
    except ValueError as exc:
        raise ValueError(f"unsupported Hathi access class: {value}") from exc


def validate_curated_seed_count(registry: HathiArchiveRegistry, observed_count: int) -> None:
    """Fail closed when a curated seed cohort changes unexpectedly."""
    if observed_count != registry.curated_seed_record_count:
        raise ValueError(
            "curated seed count drift: "
            f"expected {registry.curated_seed_record_count}, observed {observed_count}"
        )


def render_hathi_json_schema() -> dict[str, Any]:
    """Return the versioned JSON Schema for the Hathi ingestion contract."""
    item_schema = HathiArchiveItem.model_json_schema()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/edithatogo/nlp-policy-nz/schemas/hathi-ingestion-v1.json",
        "title": "HathiTrust-NZ ingestion contract",
        "version": "1.0",
        "$defs": {"HathiArchiveItem": item_schema},
        "type": "object",
        "properties": {
            "archive_item": {"$ref": "#/$defs/HathiArchiveItem"},
        },
        "required": ["archive_item"],
    }


def build_work_manifest(
    items: tuple[HathiArchiveItem, ...],
    *,
    pipeline_version: str,
    shard_size: int = 100,
) -> HathiWorkManifest:
    """Build a stable cloud work manifest from validated item rows."""
    if shard_size < 1:
        raise ValueError("shard_size must be positive")
    identities = [(item.dataset_id, item.item_id) for item in items]
    if len(identities) != len(set(identities)):
        raise ValueError("duplicate item identity")
    ordered = tuple(sorted(items, key=lambda item: (item.dataset_id, item.item_id)))
    work_items = tuple(
        HathiWorkItem(
            item_id=item.item_id,
            htid=item.htid,
            dataset_id=item.dataset_id,
            source_id=item.source_id,
            source_url=item.source_url,
            content_address=item.content_address,
            publication_decision=item.publication_decision(),
            content_allowed=item.content_allowed,
            acquisition_mode=item.acquisition_mode,
            rights_evidence=item.rights_evidence,
            derived_features_allowed=item.derived_features_allowed,
        )
        for item in ordered
    )
    shards = tuple(
        HathiWorkShard(
            shard_id=f"shard-{index:05d}",
            item_ids=tuple(work.item_id for work in work_items[start : start + shard_size]),
        )
        for index, start in enumerate(range(0, len(work_items), shard_size), start=1)
    )
    collection_ids = {item.collection_id for item in ordered}
    if len(collection_ids) > 1:
        raise ValueError("work manifest cannot mix collection ids")
    return HathiWorkManifest(
        pipeline_version=pipeline_version,
        collection_id=next(iter(collection_ids), "hathitrust-nz"),
        items=work_items,
        shards=shards,
    )


def render_work_manifest_json(manifest: HathiWorkManifest) -> str:
    """Render a deterministic JSON work manifest."""
    return (
        json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    )


__all__ = [
    "HATHI_CAPABILITY_REGISTRY",
    "AccessClass",
    "AcquisitionMode",
    "HathiArchiveItem",
    "HathiArchiveRegistry",
    "HathiDatasetDescriptor",
    "HathiRightsEvidence",
    "HathiWorkItem",
    "HathiWorkManifest",
    "HathiWorkShard",
    "PublicationDecision",
    "RightsBasis",
    "build_work_manifest",
    "hathi_capability_registry",
    "load_archive_registry",
    "render_hathi_json_schema",
    "render_work_manifest_json",
    "validate_curated_seed_count",
]
