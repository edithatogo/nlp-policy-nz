"""Provenance recording and sidecar file helpers."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

from nlp_policy_nz.provenance.serializer import serialize_prov_o_jsonld


def _utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _package_version() -> str:
    """Return the installed package version, or a local fallback."""
    try:
        return metadata.version("nlp-policy-nz")
    except metadata.PackageNotFoundError:
        return "0.0.0+local"


def _git_commit_sha() -> str:
    """Return the current Git commit SHA when available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def provenance_sidecar_path(parquet_path: str | Path) -> Path:
    """Return the sidecar path for a Parquet output."""
    path = Path(parquet_path)
    return path.with_suffix(".prov.json")


def load_provenance_sidecar(parquet_path: str | Path) -> dict[str, Any]:
    """Load PROV-O JSON-LD from a Parquet path or sidecar path."""
    path = Path(parquet_path)
    if path.suffix != ".json":
        path = provenance_sidecar_path(path)
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ProvenanceRecord:
    """Captured provenance for a single pipeline run."""

    run_id: str
    pipeline_name: str
    pipeline_version: str
    commit_sha: str
    model_versions: dict[str, str]
    parameters: dict[str, Any]
    started_at: str
    ended_at: str
    input_paths: list[str]
    output_path: str
    record_count: int
    agent_name: str = "nlp-policy-nz"
    zenodo_doi: str | None = None

    def to_jsonld(self) -> dict[str, Any]:
        """Serialize the record as PROV-O JSON-LD."""
        return serialize_prov_o_jsonld(self)

    def write_sidecar(self, parquet_path: str | Path | None = None) -> Path:
        """Write the record as a ``.prov.json`` sidecar file."""
        target = provenance_sidecar_path(parquet_path or self.output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_jsonld(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return target


@dataclass
class ProvenanceRecorder:
    """Capture execution context and produce a provenance record."""

    pipeline_name: str
    pipeline_version: str | None = None
    model_versions: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    commit_sha: str | None = None
    started_at: str = field(default_factory=_utc_now)
    agent_name: str = "nlp-policy-nz"

    def finish(
        self,
        *,
        input_paths: list[str | Path],
        output_path: str | Path,
        record_count: int,
        zenodo_doi: str | None = None,
    ) -> ProvenanceRecord:
        """Return a completed provenance record."""
        return ProvenanceRecord(
            run_id=f"urn:nlp-policy-nz:run:{self.started_at}",
            pipeline_name=self.pipeline_name,
            pipeline_version=self.pipeline_version or _package_version(),
            commit_sha=self.commit_sha or _git_commit_sha(),
            model_versions=dict(self.model_versions),
            parameters=dict(self.parameters),
            started_at=self.started_at,
            ended_at=_utc_now(),
            input_paths=[str(Path(path)) for path in input_paths],
            output_path=str(Path(output_path)),
            record_count=record_count,
            agent_name=self.agent_name,
            zenodo_doi=zenodo_doi,
        )
