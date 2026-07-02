"""Feature-flag helpers for runtime gating of pipeline stages."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class FeatureFlags:
    """Boolean gates that can disable expensive or risky pipeline behaviour."""

    enable_v1: bool = True
    enable_v2: bool = True
    embed_enabled: bool = True
    search_enabled: bool = True
    process_enabled: bool = True
    degraded_embeddings: bool = False
    kill_switch: bool = False

    def is_enabled(self, stage: str) -> bool:
        """Return whether a named pipeline stage is enabled."""
        if self.kill_switch:
            return False
        return getattr(self, f"{stage}_enabled", True)


def load_feature_flags() -> FeatureFlags:
    """Load feature flags from environment variables."""
    return FeatureFlags(
        enable_v1=_env_bool("NLP_POLICY_NZ_ENABLE_V1", True),
        enable_v2=_env_bool("NLP_POLICY_NZ_ENABLE_V2", True),
        embed_enabled=_env_bool("NLP_POLICY_NZ_ENABLE_EMBED", True),
        search_enabled=_env_bool("NLP_POLICY_NZ_ENABLE_SEARCH", True),
        process_enabled=_env_bool("NLP_POLICY_NZ_ENABLE_PROCESS", True),
        degraded_embeddings=_env_bool("NLP_POLICY_NZ_DEGRADED_EMBEDDINGS", False),
        kill_switch=_env_bool("NLP_POLICY_NZ_KILL_SWITCH", False),
    )
