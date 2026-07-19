"""Reproducible, metadata-only contracts for the historical OCR benchmark."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .benchmark import BenchmarkThresholds
from .ensemble import AdapterKind

REGISTRY_SCHEMA_VERSION: Final = "track87.ocr-engine-registry.v1"
BENCHMARK_SCHEMA_VERSION: Final = "track131.zero-cost-nz-ocr-benchmark.v1"
_DIGEST_PATTERN: Final[str] = r"^sha256:[0-9a-f]{64}$"


class RegistryEngine(BaseModel):
    """One engine identity; absent pins are allowed only for contract-only rows."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: AdapterKind
    capabilities: tuple[str, ...] = Field(min_length=1)
    requires_gpu: bool
    engine_version: str | None = None
    model_digest: str | None = Field(default=None, pattern=_DIGEST_PATTERN)
    container_digest: str | None = Field(default=None, pattern=_DIGEST_PATTERN)
    sbom_digest: str | None = Field(default=None, pattern=_DIGEST_PATTERN)
    license_spdx_id: str | None = None

    def missing_pins(self) -> tuple[str, ...]:
        """Return identity fields that prevent a reproducible engine run."""
        return tuple(
            name
            for name in (
                "engine_version",
                "model_digest",
                "container_digest",
                "sbom_digest",
                "license_spdx_id",
            )
            if getattr(self, name) in (None, "")
        )


class EngineRegistry(BaseModel):
    """Validated registry with an explicit contract-only boundary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["track87.ocr-engine-registry.v1"]
    status: Literal["adapter_contract_only", "benchmark_ready"]
    publication_rule: str = Field(min_length=1)
    engines: tuple[RegistryEngine, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_engine_set(self) -> EngineRegistry:
        """Reject duplicate engine identities and unpinned ready registries."""
        kinds = tuple(engine.kind for engine in self.engines)
        if len(set(kinds)) != len(kinds):
            raise ValueError("engine registry contains duplicate kinds")
        if self.status == "benchmark_ready":
            validate_immutable_pins(self)
        return self


def validate_immutable_pins(registry: EngineRegistry) -> None:
    """Fail closed unless every engine has all required immutable identities."""
    missing = {
        engine.kind.value: engine.missing_pins()
        for engine in registry.engines
        if engine.missing_pins()
    }
    if missing:
        details = "; ".join(
            f"{kind}: {', '.join(fields)}" for kind, fields in sorted(missing.items())
        )
        raise ValueError(f"immutable engine pins are incomplete ({details})")


class BenchmarkManifest(BaseModel):
    """Metadata-only run specification for a reproducible benchmark."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["track131.zero-cost-nz-ocr-benchmark.v1"]
    benchmark_id: str = Field(min_length=1)
    pipeline_version: str = Field(min_length=1)
    registry_path: str = Field(min_length=1)
    fixture_path: str = Field(min_length=1)
    compute_policy: Literal["no_cost_only"]
    case_ids: tuple[str, ...] = Field(min_length=1)
    metrics: tuple[str, ...] = Field(min_length=1)
    thresholds: BenchmarkThresholds


class BenchmarkScaffold(BaseModel):
    """Deterministic report shell that makes missing evidence visible."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["track131.zero-cost-nz-ocr-benchmark.v1"]
    benchmark_id: str
    status: Literal["not_run"]
    compute_policy: Literal["no_cost_only"]
    registry_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    fixture_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    engine_status: dict[str, Literal["adapter_contract_only", "blocked_unpinned"]]
    blockers: tuple[str, ...]
    claim_boundary: str


def load_registry(path: Path | str) -> EngineRegistry:
    """Load and validate a JSON registry without performing any engine work."""
    return EngineRegistry.model_validate_json(Path(path).read_text(encoding="utf-8"))


def load_manifest(path: Path | str) -> BenchmarkManifest:
    """Load and validate a benchmark manifest."""
    return BenchmarkManifest.model_validate_json(Path(path).read_text(encoding="utf-8"))


def build_scaffold(
    manifest: BenchmarkManifest,
    registry: EngineRegistry,
    fixture_payload: Mapping[str, object],
) -> BenchmarkScaffold:
    """Build a stable not-run report from metadata and content hashes only."""
    if set(manifest.case_ids) != {
        str(case.get("case_id"))
        for case in fixture_payload.get("cases", [])
        if isinstance(case, Mapping)
    }:
        raise ValueError("benchmark manifest case_ids must match fixture case ids")
    registry_bytes = _canonical_json(registry.model_dump(mode="json"))
    fixture_bytes = _canonical_json(fixture_payload)
    statuses = {
        engine.kind.value: (
            "blocked_unpinned" if engine.missing_pins() else "adapter_contract_only"
        )
        for engine in registry.engines
    }
    blockers = tuple(
        sorted(
            {
                f"{engine.kind.value}: missing {', '.join(engine.missing_pins())}"
                for engine in registry.engines
                if engine.missing_pins()
            }
        )
    )
    return BenchmarkScaffold(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        benchmark_id=manifest.benchmark_id,
        status="not_run",
        compute_policy=manifest.compute_policy,
        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
        fixture_sha256=hashlib.sha256(fixture_bytes).hexdigest(),
        engine_status=statuses,
        blockers=blockers,
        claim_boundary=(
            "Metadata-only scaffold. No page images, OCR outputs, measured metrics, "
            "engine promotion, or paid compute claim is made."
        ),
    )


def write_scaffold(report: BenchmarkScaffold, path: Path | str) -> Path:
    """Write canonical, newline-terminated JSON for artifact comparison."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def _canonical_json(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


__all__ = [
    "BENCHMARK_SCHEMA_VERSION",
    "BenchmarkManifest",
    "BenchmarkScaffold",
    "EngineRegistry",
    "RegistryEngine",
    "build_scaffold",
    "load_manifest",
    "load_registry",
    "validate_immutable_pins",
    "write_scaffold",
]
