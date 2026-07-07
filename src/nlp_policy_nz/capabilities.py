"""Capability registry and contract helpers for NLP Policy NZ.

This module defines the machine-readable contract surface for the package:
current CLI commands, HTTP API routes, SDK helpers, and planned MCP tools.
It stays on the standard library so it is deterministic and easy to validate
in GitHub Actions without any optional runtime dependencies.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable


_STABLE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")


class CapabilitySurface(StrEnum):
    """Top-level capability surface classification."""

    CLI = "cli"
    API = "api"
    SDK = "sdk"
    MCP = "mcp"


class CapabilityMaturity(StrEnum):
    """Lifecycle state for a capability entry."""

    CURRENT = "current"
    FUTURE = "future"


class CapabilityClassification(StrEnum):
    """Audience/classification metadata for a capability entry."""

    PUBLIC = "public"
    INTERNAL = "internal"
    FUTURE = "future"


@dataclass(frozen=True, slots=True)
class CapabilityEntry:
    """Single contract surface entry in the capability registry."""

    id: str
    surface: CapabilitySurface
    name: str
    summary: str
    maturity: CapabilityMaturity
    classification: CapabilityClassification
    required_fields: tuple[str, ...]
    implementation_ref: str
    contract_kind: str
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_entry(self)

    def to_dict(self) -> dict[str, Any]:
        """Convert the entry to a JSON-serialisable mapping."""

        return {
            "id": self.id,
            "surface": self.surface.value,
            "name": self.name,
            "summary": self.summary,
            "maturity": self.maturity.value,
            "classification": self.classification.value,
            "required_fields": list(self.required_fields),
            "implementation_ref": self.implementation_ref,
            "contract_kind": self.contract_kind,
            "aliases": list(self.aliases),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CapabilityEntry:
        """Build an entry from a machine-readable payload."""

        return cls(
            id=str(payload["id"]),
            surface=CapabilitySurface(str(payload["surface"])),
            name=str(payload["name"]),
            summary=str(payload["summary"]),
            maturity=CapabilityMaturity(str(payload["maturity"])),
            classification=CapabilityClassification(str(payload["classification"])),
            required_fields=tuple(str(value) for value in payload.get("required_fields", ())),
            implementation_ref=str(payload["implementation_ref"]),
            contract_kind=str(payload["contract_kind"]),
            aliases=tuple(str(value) for value in payload.get("aliases", ())),
        )


@dataclass(frozen=True, slots=True)
class CapabilityRegistry:
    """Validated registry of current and planned capability entries."""

    entries: tuple[CapabilityEntry, ...]
    schema_version: int = 1
    source: str = "nlp_policy_nz.capabilities"

    def __post_init__(self) -> None:
        validate_capability_entries(self.entries)

    def to_dict(self) -> dict[str, Any]:
        """Convert the registry to a deterministic JSON-compatible mapping."""

        return {
            "schema_version": self.schema_version,
            "source": self.source,
            "entry_count": len(self.entries),
            "entries": [entry.to_dict() for entry in self.entries],
        }

    def to_json(self) -> str:
        """Render the registry as canonical JSON."""

        return json.dumps(self.to_dict(), indent=2, sort_keys=True, ensure_ascii=False)

    def write_json(self, path: str | Path) -> Path:
        """Write the registry JSON to *path* and return the resolved target."""

        target = Path(path)
        target.write_text(self.to_json() + "\n", encoding="utf-8")
        return target

    def ids(self) -> tuple[str, ...]:
        """Return the stable IDs in registry order."""

        return tuple(entry.id for entry in self.entries)

    def by_surface(self, surface: CapabilitySurface) -> tuple[CapabilityEntry, ...]:
        """Return entries for a given surface in registry order."""

        return tuple(entry for entry in self.entries if entry.surface == surface)

    def surfaces(self) -> tuple[CapabilitySurface, ...]:
        """Return the distinct surfaces covered by the registry."""

        seen: set[CapabilitySurface] = set()
        ordered: list[CapabilitySurface] = []
        for entry in self.entries:
            if entry.surface in seen:
                continue
            seen.add(entry.surface)
            ordered.append(entry.surface)
        return tuple(ordered)

    def missing_surfaces(
        self,
        required: Iterable[CapabilitySurface] = (
            CapabilitySurface.CLI,
            CapabilitySurface.API,
            CapabilitySurface.SDK,
            CapabilitySurface.MCP,
        ),
    ) -> tuple[CapabilitySurface, ...]:
        """Return required surfaces that are not represented in the registry."""

        present = set(self.surfaces())
        return tuple(surface for surface in required if surface not in present)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> CapabilityRegistry:
        """Build a registry from a machine-readable payload."""

        entries_payload = payload.get("entries", ())
        entries = tuple(CapabilityEntry.from_dict(item) for item in entries_payload)
        return cls(
            entries=entries,
            schema_version=int(payload.get("schema_version", 1)),
            source=str(payload.get("source", "nlp_policy_nz.capabilities")),
        )

    @classmethod
    def from_json(cls, payload: str) -> CapabilityRegistry:
        """Build a registry from JSON text."""

        return cls.from_dict(json.loads(payload))


def validate_capability_entries(entries: Iterable[CapabilityEntry]) -> tuple[CapabilityEntry, ...]:
    """Validate stable IDs and uniqueness for a sequence of entries."""

    validated = tuple(entries)
    if not validated:
        raise ValueError("Capability registry must contain at least one entry")

    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in validated:
        if not _STABLE_ID_PATTERN.fullmatch(entry.id):
            raise ValueError(
                f"Capability ID {entry.id!r} is not stable; use lowercase dotted identifiers."
            )
        if entry.id in seen:
            duplicates.append(entry.id)
            continue
        seen.add(entry.id)

    if duplicates:
        unique_duplicates = ", ".join(sorted(set(duplicates)))
        raise ValueError(f"Duplicate capability IDs: {unique_duplicates}")

    return validated


def validate_capability_registry(
    registry: CapabilityRegistry,
    *,
    required_surfaces: Iterable[CapabilitySurface] = (
        CapabilitySurface.CLI,
        CapabilitySurface.API,
        CapabilitySurface.SDK,
        CapabilitySurface.MCP,
    ),
) -> CapabilityRegistry:
    """Validate registry uniqueness and required surface coverage."""

    missing = registry.missing_surfaces(required_surfaces)
    if missing:
        names = ", ".join(surface.value for surface in missing)
        raise ValueError(f"Capability registry is missing required surfaces: {names}")
    return registry


def load_capability_registry(path: str | Path | None = None) -> CapabilityRegistry:
    """Load a registry from JSON or return the checked-in default registry."""

    if path is None:
        return validate_capability_registry(DEFAULT_CAPABILITY_REGISTRY)
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_capability_registry(CapabilityRegistry.from_dict(payload))


def dump_capability_registry(registry: CapabilityRegistry, path: str | Path) -> Path:
    """Persist a registry to disk in canonical JSON form."""

    return registry.write_json(path)


def _validate_entry(entry: CapabilityEntry) -> None:
    if not _STABLE_ID_PATTERN.fullmatch(entry.id):
        raise ValueError(
            f"Capability ID {entry.id!r} is not stable; use lowercase dotted identifiers."
        )
    if not entry.name.strip():
        raise ValueError(f"Capability {entry.id!r} is missing a name")
    if not entry.summary.strip():
        raise ValueError(f"Capability {entry.id!r} is missing a summary")
    if not entry.implementation_ref.strip():
        raise ValueError(f"Capability {entry.id!r} is missing an implementation_ref")
    if not entry.contract_kind.strip():
        raise ValueError(f"Capability {entry.id!r} is missing a contract_kind")
    if len(set(entry.required_fields)) != len(entry.required_fields):
        raise ValueError(f"Capability {entry.id!r} has duplicate required_fields entries")
    if len(set(entry.aliases)) != len(entry.aliases):
        raise ValueError(f"Capability {entry.id!r} has duplicate aliases")
    if entry.id in entry.aliases:
        raise ValueError(f"Capability {entry.id!r} must not alias itself")


def _entry(
    *,
    id: str,
    surface: CapabilitySurface,
    name: str,
    summary: str,
    maturity: CapabilityMaturity,
    classification: CapabilityClassification,
    required_fields: tuple[str, ...],
    implementation_ref: str,
    contract_kind: str,
    aliases: tuple[str, ...] = (),
) -> CapabilityEntry:
    return CapabilityEntry(
        id=id,
        surface=surface,
        name=name,
        summary=summary,
        maturity=maturity,
        classification=classification,
        required_fields=required_fields,
        implementation_ref=implementation_ref,
        contract_kind=contract_kind,
        aliases=aliases,
    )


DEFAULT_CAPABILITY_REGISTRY = CapabilityRegistry(
    entries=(
        # CLI
        _entry(
            id="cli.process",
            surface=CapabilitySurface.CLI,
            name="Process corpus documents",
            summary="Run the batch pipeline over legislation or Hansard inputs.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input", "output", "source"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#process",
            contract_kind="command",
        ),
        _entry(
            id="cli.search",
            surface=CapabilitySurface.CLI,
            name="Search the vector index",
            summary="Search LanceDB with a natural-language query.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("query",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#search",
            contract_kind="command",
        ),
        _entry(
            id="cli.upload-dataset",
            surface=CapabilitySurface.CLI,
            name="Upload a dataset",
            summary="Convert a Parquet output into a Hugging Face dataset upload.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet", "repo_id"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#upload-dataset",
            contract_kind="command",
        ),
        _entry(
            id="cli.auth.create-key",
            surface=CapabilitySurface.CLI,
            name="Create an API key",
            summary="Mint a new hashed API key with explicit scopes.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.INTERNAL,
            required_fields=("name", "scopes"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#auth.create-key",
            contract_kind="command",
        ),
        _entry(
            id="cli.auth.list-keys",
            surface=CapabilitySurface.CLI,
            name="List API keys",
            summary="Inspect stored API key metadata without revealing secrets.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.INTERNAL,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/cli/main.py#auth.list-keys",
            contract_kind="command",
        ),
        _entry(
            id="cli.auth.revoke-key",
            surface=CapabilitySurface.CLI,
            name="Revoke an API key",
            summary="Deactivate a stored API key by identifier.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.INTERNAL,
            required_fields=("key_id",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#auth.revoke-key",
            contract_kind="command",
        ),
        _entry(
            id="cli.auth.rotate-key",
            surface=CapabilitySurface.CLI,
            name="Rotate an API key",
            summary="Revoke an existing key and mint a replacement.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.INTERNAL,
            required_fields=("key_id",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#auth.rotate-key",
            contract_kind="command",
        ),
        _entry(
            id="cli.deploy-space",
            surface=CapabilitySurface.CLI,
            name="Deploy a Hugging Face Space",
            summary="Publish the Gradio demo space to Hugging Face Hub.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("repo_id",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#deploy-space",
            contract_kind="command",
        ),
        _entry(
            id="cli.archive-to-zenodo",
            surface=CapabilitySurface.CLI,
            name="Archive to Zenodo Sandbox",
            summary="Upload a Parquet artifact to Zenodo Sandbox and publish it.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet", "title", "description", "creators"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#archive-to-zenodo",
            contract_kind="command",
        ),
        _entry(
            id="cli.release",
            surface=CapabilitySurface.CLI,
            name="Create a versioned release",
            summary="Build a release archive and publish the deposit.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet", "version", "title", "description", "creators"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#release",
            contract_kind="command",
        ),
        _entry(
            id="cli.provenance",
            surface=CapabilitySurface.CLI,
            name="Display provenance",
            summary="Print the PROV-O sidecar for a generated Parquet file.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#provenance",
            contract_kind="command",
        ),
        _entry(
            id="cli.export-rdf",
            surface=CapabilitySurface.CLI,
            name="Export RDF",
            summary="Write SIOC/FOAF Turtle from Hansard outputs.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#export-rdf",
            contract_kind="command",
        ),
        _entry(
            id="cli.sparql",
            surface=CapabilitySurface.CLI,
            name="Run SPARQL",
            summary="Query a local Turtle graph with SPARQL SELECT.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("rdf", "query"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#sparql",
            contract_kind="command",
        ),
        _entry(
            id="cli.knowledge-graph",
            surface=CapabilitySurface.CLI,
            name="Export a knowledge graph",
            summary="Write schema.org JSON-LD from resolved entities.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("entities", "output"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#knowledge-graph",
            contract_kind="command",
        ),
        _entry(
            id="cli.voting-summary",
            surface=CapabilitySurface.CLI,
            name="Summarise a division",
            summary="Parse Hansard division text into vote summary output.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#voting-summary",
            contract_kind="command",
        ),
        _entry(
            id="cli.amendment-history",
            surface=CapabilitySurface.CLI,
            name="Extract amendment history",
            summary="Parse amendment records from Hansard or committee text.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#amendment-history",
            contract_kind="command",
        ),
        _entry(
            id="cli.rac-export",
            surface=CapabilitySurface.CLI,
            name="Export rules-as-code bridges",
            summary="Build a source-grounded JSON-LD bridge record and package.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input", "output", "citation_path", "source_url", "retrieved_at"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#rac-export",
            contract_kind="command",
        ),
        _entry(
            id="cli.policyengine-pilot",
            surface=CapabilitySurface.CLI,
            name="Build the PolicyEngine pilot",
            summary="Generate the Track 79 pilot package from the reviewed manifest.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("manifest", "output_dir"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#policyengine-pilot",
            contract_kind="command",
        ),
        _entry(
            id="cli.multi-engine-parity",
            surface=CapabilitySurface.CLI,
            name="Build the parity bundle",
            summary="Generate the Track 80 parity bundle and report.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("manifest", "output_dir"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#multi-engine-parity",
            contract_kind="command",
        ),
        _entry(
            id="cli.export-extractions",
            surface=CapabilitySurface.CLI,
            name="Export extraction manifests",
            summary="Convert Parquet output into deterministic extraction JSON.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet", "output", "retrieved_at"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#export-extractions",
            contract_kind="command",
        ),
        _entry(
            id="cli.export-rac-candidates",
            surface=CapabilitySurface.CLI,
            name="Export rules-as-code candidates",
            summary="Build batch candidate manifests from fixtures or Parquet rows.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#export-rac-candidates",
            contract_kind="command",
        ),
        _entry(
            id="cli.export-nz-ontologies",
            surface=CapabilitySurface.CLI,
            name="Export NZ ontologies",
            summary="Write Track 31 ontology artifacts and controlled vocabularies.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#export-nz-ontologies",
            contract_kind="command",
        ),
        _entry(
            id="cli.corpus-stats",
            surface=CapabilitySurface.CLI,
            name="Export corpus statistics",
            summary="Compute Track 32 descriptive corpus statistics.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#corpus-stats",
            contract_kind="command",
        ),
        _entry(
            id="cli.graph-vector-analysis",
            surface=CapabilitySurface.CLI,
            name="Export graph and vector analysis",
            summary="Compute Track 33 graph topology and vector metrics.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#graph-vector-analysis",
            contract_kind="command",
        ),
        _entry(
            id="cli.publication-protocol",
            surface=CapabilitySurface.CLI,
            name="Export the publication protocol",
            summary="Write Track 34 claim-evidence and reproducibility artifacts.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#publication-protocol",
            contract_kind="command",
        ),
        _entry(
            id="cli.generate-analysis-artifacts",
            surface=CapabilitySurface.CLI,
            name="Generate analysis artifacts",
            summary="Build tables, figures, diagrams, and blocker manifests.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#generate-analysis-artifacts",
            contract_kind="command",
        ),
        _entry(
            id="cli.generate-manuscript-package",
            surface=CapabilitySurface.CLI,
            name="Generate the manuscript package",
            summary="Write the manuscript scaffold, review rubric, and support files.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("output_dir",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#generate-manuscript-package",
            contract_kind="command",
        ),
        _entry(
            id="cli.quality.validate",
            surface=CapabilitySurface.CLI,
            name="Validate inputs",
            summary="Check ingestion inputs before processing.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#quality.validate",
            contract_kind="command",
        ),
        _entry(
            id="cli.quality.report",
            surface=CapabilitySurface.CLI,
            name="Render a quality report",
            summary="Generate a batch quality report from Parquet inputs.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("parquet", "output"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#quality.report",
            contract_kind="command",
        ),
        _entry(
            id="cli.quality.dashboard",
            surface=CapabilitySurface.CLI,
            name="Render a quality dashboard",
            summary="Write a static HTML dashboard from historical reports.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("history_dir", "output"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#quality.dashboard",
            contract_kind="command",
        ),
        _entry(
            id="cli.quality.alert",
            surface=CapabilitySurface.CLI,
            name="Evaluate quality alerts",
            summary="Check the latest report against the configured threshold.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("history_dir", "threshold"),
            implementation_ref="src/nlp_policy_nz/cli/main.py#quality.alert",
            contract_kind="command",
        ),
        _entry(
            id="cli.completion.install",
            surface=CapabilitySurface.CLI,
            name="Generate shell completions",
            summary="Render installable completion scripts for supported shells.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("shell",),
            implementation_ref="src/nlp_policy_nz/cli/main.py#completion.install",
            contract_kind="command",
        ),
        _entry(
            id="cli.completion.manpage",
            surface=CapabilitySurface.CLI,
            name="Generate a man page",
            summary="Render a roff man page from the CLI parser.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/cli/main.py#completion.manpage",
            contract_kind="command",
        ),
        # API
        _entry(
            id="api.health",
            surface=CapabilitySurface.API,
            name="Health check",
            summary="Expose service health and model-load status.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/api/server.py#/health",
            contract_kind="http_route",
            aliases=("api.v1.health", "api.v2.health"),
        ),
        _entry(
            id="api.startup",
            surface=CapabilitySurface.API,
            name="Startup probe",
            summary="Report startup completion state.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/api/server.py#/startup",
            contract_kind="http_route",
        ),
        _entry(
            id="api.ready",
            surface=CapabilitySurface.API,
            name="Readiness probe",
            summary="Report service readiness for requests.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/api/server.py#/ready",
            contract_kind="http_route",
        ),
        _entry(
            id="api.live",
            surface=CapabilitySurface.API,
            name="Liveness probe",
            summary="Report simple process liveness.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/api/server.py#/live",
            contract_kind="http_route",
        ),
        _entry(
            id="api.version",
            surface=CapabilitySurface.API,
            name="Version metadata",
            summary="Expose the canonical release version metadata.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/api/server.py#/version",
            contract_kind="http_route",
            aliases=("api.v1.version", "api.v2.version"),
        ),
        _entry(
            id="api.metrics",
            surface=CapabilitySurface.API,
            name="Metrics endpoint",
            summary="Expose Prometheus-compatible metrics.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.INTERNAL,
            required_fields=(),
            implementation_ref="src/nlp_policy_nz/api/server.py#/metrics",
            contract_kind="http_route",
        ),
        _entry(
            id="api.embed",
            surface=CapabilitySurface.API,
            name="Generate embeddings",
            summary="Create embeddings for one or more input texts.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("texts",),
            implementation_ref="src/nlp_policy_nz/api/server.py#/embed",
            contract_kind="http_route",
            aliases=("api.v1.embed", "api.v2.embed"),
        ),
        _entry(
            id="api.search",
            surface=CapabilitySurface.API,
            name="Semantic search",
            summary="Run vector search over the configured index.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("query",),
            implementation_ref="src/nlp_policy_nz/api/server.py#/search",
            contract_kind="http_route",
            aliases=("api.v1.search", "api.v2.search"),
        ),
        _entry(
            id="api.process",
            surface=CapabilitySurface.API,
            name="Run the full pipeline",
            summary="Process inline or file-based input through the pipeline.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input",),
            implementation_ref="src/nlp_policy_nz/api/server.py#/process",
            contract_kind="http_route",
            aliases=("api.v1.process", "api.v2.process"),
        ),
        # SDK
        _entry(
            id="sdk.process-hansard",
            surface=CapabilitySurface.SDK,
            name="Process Hansard",
            summary="Run the Hansard pipeline from Python.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input_path", "output_path"),
            implementation_ref="src/nlp_policy_nz/pipeline_api.py#process_hansard",
            contract_kind="python_function",
        ),
        _entry(
            id="sdk.process-legislation",
            surface=CapabilitySurface.SDK,
            name="Process legislation",
            summary="Run the legislation pipeline from Python.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("input_path", "output_path"),
            implementation_ref="src/nlp_policy_nz/pipeline_api.py#process_legislation",
            contract_kind="python_function",
        ),
        _entry(
            id="sdk.search-similar",
            surface=CapabilitySurface.SDK,
            name="Search similar documents",
            summary="Search the vector index from Python code.",
            maturity=CapabilityMaturity.CURRENT,
            classification=CapabilityClassification.PUBLIC,
            required_fields=("query",),
            implementation_ref="src/nlp_policy_nz/pipeline_api.py#search_similar",
            contract_kind="python_function",
        ),
        # MCP - future capabilities only
        _entry(
            id="mcp.registry.list",
            surface=CapabilitySurface.MCP,
            name="List capabilities",
            summary="Expose the registry to MCP clients.",
            maturity=CapabilityMaturity.FUTURE,
            classification=CapabilityClassification.FUTURE,
            required_fields=(),
            implementation_ref="docs/capabilities.md#mcp-registry",
            contract_kind="mcp_tool",
        ),
        _entry(
            id="mcp.registry.validate",
            surface=CapabilitySurface.MCP,
            name="Validate a capability payload",
            summary="Validate registry payloads before they are accepted.",
            maturity=CapabilityMaturity.FUTURE,
            classification=CapabilityClassification.FUTURE,
            required_fields=("registry",),
            implementation_ref="docs/capabilities.md#mcp-validation",
            contract_kind="mcp_tool",
        ),
        _entry(
            id="mcp.pipeline.process",
            surface=CapabilitySurface.MCP,
            name="Trigger pipeline processing",
            summary="Plan a future MCP tool for document processing.",
            maturity=CapabilityMaturity.FUTURE,
            classification=CapabilityClassification.FUTURE,
            required_fields=("input", "source"),
            implementation_ref="docs/capabilities.md#mcp-pipeline",
            contract_kind="mcp_tool",
        ),
        _entry(
            id="mcp.pipeline.search",
            surface=CapabilitySurface.MCP,
            name="Search processed outputs",
            summary="Plan a future MCP tool for semantic search.",
            maturity=CapabilityMaturity.FUTURE,
            classification=CapabilityClassification.FUTURE,
            required_fields=("query",),
            implementation_ref="docs/capabilities.md#mcp-pipeline",
            contract_kind="mcp_tool",
        ),
    ),
)
