"""Runtime settings for API versioning, CORS, and deployment hardening."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_list(name: str, default: list[str]) -> list[str]:
    value = os.getenv(name)
    if not value:
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    """Runtime knobs for deployment and production hardening."""

    api_versions: tuple[str, ...] = ("v1", "v2")
    cors_origins: tuple[str, ...] = ("*",)
    db_path: str = "./lancedb_data"
    last_run_timestamp: str | None = None
    rate_limit_per_minute: int = 60
    uvicorn_workers: int = 1
    sunset_days_v1: int = 180


def load_runtime_settings() -> RuntimeSettings:
    """Load runtime settings from environment variables."""
    api_versions = tuple(_env_list("NLP_POLICY_NZ_API_VERSIONS", ["v1", "v2"]))
    cors_origins = tuple(_env_list("NLP_POLICY_NZ_CORS_ORIGINS", ["*"]))
    last_run_timestamp = os.getenv("NLP_POLICY_NZ_LAST_RUN_TIMESTAMP") or None
    return RuntimeSettings(
        api_versions=api_versions,
        cors_origins=cors_origins,
        db_path=os.getenv("NLP_POLICY_NZ_DB_PATH", "./lancedb_data"),
        last_run_timestamp=last_run_timestamp,
        rate_limit_per_minute=_env_int("NLP_POLICY_NZ_RATE_LIMIT_PER_MINUTE", 60),
        uvicorn_workers=_env_int("NLP_POLICY_NZ_UVICORN_WORKERS", 1),
        sunset_days_v1=_env_int("NLP_POLICY_NZ_V1_SUNSET_DAYS", 180),
    )
