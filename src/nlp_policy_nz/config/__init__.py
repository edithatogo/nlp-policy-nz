"""Runtime configuration helpers for production hardening."""

from __future__ import annotations

from nlp_policy_nz.config.feature_flags import FeatureFlags, load_feature_flags
from nlp_policy_nz.config.jurisdiction_activation import (
    ProfileActivationGrant,
    ProfileActivationRegistry,
    canonical_activation_registry_digest,
    load_profile_activation_registry,
)
from nlp_policy_nz.config.jurisdiction_profiles import (
    CapabilityStatus,
    CorpusProfile,
    JurisdictionProfile,
    OntologyPin,
    ProfileCapability,
    ProfileLoadError,
    ProfileRegistry,
    ProfileResolution,
    ProfileStatus,
    canonical_profile_digest,
    load_jurisdiction_profile,
    load_jurisdiction_profiles,
)
from nlp_policy_nz.config.runtime import RuntimeSettings, load_runtime_settings

__all__ = [
    "CapabilityStatus",
    "CorpusProfile",
    "FeatureFlags",
    "JurisdictionProfile",
    "OntologyPin",
    "ProfileActivationGrant",
    "ProfileActivationRegistry",
    "ProfileCapability",
    "ProfileLoadError",
    "ProfileRegistry",
    "ProfileResolution",
    "ProfileStatus",
    "RuntimeSettings",
    "canonical_activation_registry_digest",
    "canonical_profile_digest",
    "load_feature_flags",
    "load_jurisdiction_profile",
    "load_jurisdiction_profiles",
    "load_profile_activation_registry",
    "load_runtime_settings",
]
