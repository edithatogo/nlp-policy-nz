"""Shared interface contract for the public `nlp-policy-nz` surfaces.

The contract keeps the CLI, HTTP API, client SDK, and MCP adapter aligned
around a common set of capabilities. It is intentionally lightweight and
deterministic so it can be validated in GitHub Actions without optional model
dependencies.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class SurfaceKind(StrEnum):
    """Public-facing surface where a capability is exposed."""

    CLI = "cli"
    API = "api"
    SDK = "sdk"
    REPORT = "report"
    MCP = "mcp"


class SideEffectLevel(StrEnum):
    """Operational side-effect classification for a capability."""

    READ_ONLY = "read_only"
    LOCAL_WRITE = "local_write"
    PUBLISH = "publish"
    EXTERNAL_NETWORK = "external_network"


class AuthRequirement(StrEnum):
    """Authentication or scope requirement for a capability."""

    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"


@dataclass(slots=True, frozen=True)
class CapabilityRecord:
    """Description of one exposed capability."""

    capability_id: str
    title: str
    surface: SurfaceKind
    owner_module: str
    description: str
    side_effect: SideEffectLevel
    auth_requirement: AuthRequirement = AuthRequirement.NONE
    auth_scope: str | None = None
    legal_review_boundary: bool = False
    github_actions_safe: bool = True
    input_schema: str | None = None
    output_schema: str | None = None
    version: str = "v1"
    experimental: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialise the record into JSON-compatible data."""
        data = asdict(self)
        data["surface"] = self.surface.value
        data["side_effect"] = self.side_effect.value
        data["auth_requirement"] = self.auth_requirement.value
        return data


@dataclass(slots=True, frozen=True)
class InterfaceContract:
    """Versioned collection of public capabilities."""

    contract_id: str
    contract_version: str
    generated_from: str
    capabilities: tuple[CapabilityRecord, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        ids = [record.capability_id for record in self.capabilities]
        if len(ids) != len(set(ids)):
            msg = "Capability IDs must be unique."
            raise ValueError(msg)

    def to_dict(self) -> dict[str, Any]:
        """Serialise the contract for storage or transport."""
        return {
            "contract_id": self.contract_id,
            "contract_version": self.contract_version,
            "generated_from": self.generated_from,
            "capabilities": [record.to_dict() for record in self.capabilities],
        }

    def lookup(self, capability_id: str) -> CapabilityRecord:
        """Return a capability by ID."""
        for record in self.capabilities:
            if record.capability_id == capability_id:
                return record
        msg = f"Unknown capability_id: {capability_id}"
        raise KeyError(msg)

    def filter(self, *, surface: SurfaceKind | None = None) -> tuple[CapabilityRecord, ...]:
        """Return capabilities matching an optional surface filter."""
        records = self.capabilities
        if surface is None:
            return records
        return tuple(record for record in records if record.surface == surface)

    def validate(self) -> None:
        """Raise if the contract contains inconsistent metadata."""
        for record in self.capabilities:
            if not record.capability_id.strip():
                msg = "Capability IDs must not be blank."
                raise ValueError(msg)
            if not record.title.strip():
                msg = f"Capability {record.capability_id} is missing a title."
                raise ValueError(msg)
            if not record.owner_module.strip():
                msg = f"Capability {record.capability_id} is missing an owner module."
                raise ValueError(msg)
            if (
                record.side_effect in {
                    SideEffectLevel.PUBLISH,
                    SideEffectLevel.EXTERNAL_NETWORK,
                }
                and record.auth_requirement == AuthRequirement.NONE
            ):
                msg = f"Capability {record.capability_id} has a non-read-only side effect but no auth requirement."
                raise ValueError(msg)
            if record.auth_requirement != AuthRequirement.NONE and not record.auth_scope:
                msg = f"Capability {record.capability_id} requires auth but has no auth scope."
                raise ValueError(msg)


def _capability(
    capability_id: str,
    title: str,
    *,
    surface: SurfaceKind,
    owner_module: str,
    description: str,
    side_effect: SideEffectLevel,
    auth_requirement: AuthRequirement = AuthRequirement.NONE,
    auth_scope: str | None = None,
    legal_review_boundary: bool = False,
    github_actions_safe: bool = True,
    input_schema: str | None = None,
    output_schema: str | None = None,
    experimental: bool = False,
) -> CapabilityRecord:
    return CapabilityRecord(
        capability_id=capability_id,
        title=title,
        surface=surface,
        owner_module=owner_module,
        description=description,
        side_effect=side_effect,
        auth_requirement=auth_requirement,
        auth_scope=auth_scope,
        legal_review_boundary=legal_review_boundary,
        github_actions_safe=github_actions_safe,
        input_schema=input_schema,
        output_schema=output_schema,
        experimental=experimental,
    )


DEFAULT_INTERFACE_CONTRACT = InterfaceContract(
    contract_id="nlp-policy-nz.interface-contract.v1",
    contract_version="v1",
    generated_from="src/nlp_policy_nz/interface_contract.py",
    capabilities=(
        _capability(
            "cli.process",
            "Process corpus documents",
            surface=SurfaceKind.CLI,
            owner_module="nlp_policy_nz.cli.main",
            description="Process legislation or Hansard through the core pipeline.",
            side_effect=SideEffectLevel.LOCAL_WRITE,
            input_schema="ProcessRequest",
            output_schema="ProcessResponse",
        ),
        _capability(
            "cli.search",
            "Search the local vector index",
            surface=SurfaceKind.CLI,
            owner_module="nlp_policy_nz.cli.main",
            description="Search LanceDB-backed local corpus outputs.",
            side_effect=SideEffectLevel.READ_ONLY,
            input_schema="SearchRequest",
            output_schema="SearchResponse",
        ),
        _capability(
            "cli.publish",
            "Upload datasets and releases",
            surface=SurfaceKind.CLI,
            owner_module="nlp_policy_nz.cli.main",
            description="Publish datasets, spaces, Zenodo archives, and releases.",
            side_effect=SideEffectLevel.PUBLISH,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="publish",
            github_actions_safe=False,
        ),
        _capability(
            "api.health",
            "API health check",
            surface=SurfaceKind.API,
            owner_module="nlp_policy_nz.api.server",
            description="Check runtime and model readiness.",
            side_effect=SideEffectLevel.READ_ONLY,
            input_schema="HealthResponse",
            output_schema="HealthResponse",
        ),
        _capability(
            "api.version",
            "API version metadata",
            surface=SurfaceKind.API,
            owner_module="nlp_policy_nz.api.server",
            description="Return version, build, and dataset metadata.",
            side_effect=SideEffectLevel.READ_ONLY,
            input_schema="VersionResponse",
            output_schema="VersionResponse",
        ),
        _capability(
            "api.embed",
            "Generate embeddings",
            surface=SurfaceKind.API,
            owner_module="nlp_policy_nz.api.server",
            description="Generate embeddings for a batch of texts.",
            side_effect=SideEffectLevel.LOCAL_WRITE,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            input_schema="EmbedRequest",
            output_schema="EmbedResponse",
        ),
        _capability(
            "api.search",
            "Search corpus via HTTP",
            surface=SurfaceKind.API,
            owner_module="nlp_policy_nz.api.server",
            description="Search local vector data through the HTTP API.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            input_schema="SearchRequest",
            output_schema="SearchResponse",
        ),
        _capability(
            "api.process",
            "Process text via HTTP",
            surface=SurfaceKind.API,
            owner_module="nlp_policy_nz.api.server",
            description="Run the core pipeline over inline text or input files.",
            side_effect=SideEffectLevel.LOCAL_WRITE,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="write",
            input_schema="ProcessRequest",
            output_schema="ProcessResponse",
        ),
        _capability(
            "sdk.health",
            "SDK health call",
            surface=SurfaceKind.SDK,
            owner_module="nlp_policy_nz.client.sync",
            description="Typed client method for health checks.",
            side_effect=SideEffectLevel.READ_ONLY,
            input_schema="HealthResponse",
            output_schema="HealthResponse",
        ),
        _capability(
            "sdk.version",
            "SDK version call",
            surface=SurfaceKind.SDK,
            owner_module="nlp_policy_nz.client.sync",
            description="Typed client method for version metadata.",
            side_effect=SideEffectLevel.READ_ONLY,
            input_schema="VersionResponse",
            output_schema="VersionResponse",
        ),
        _capability(
            "sdk.embed",
            "SDK embed call",
            surface=SurfaceKind.SDK,
            owner_module="nlp_policy_nz.client.sync",
            description="Typed client method for embedding generation.",
            side_effect=SideEffectLevel.LOCAL_WRITE,
            input_schema="EmbedRequest",
            output_schema="EmbedResponse",
        ),
        _capability(
            "sdk.search",
            "SDK search call",
            surface=SurfaceKind.SDK,
            owner_module="nlp_policy_nz.client.sync",
            description="Typed client method for semantic search.",
            side_effect=SideEffectLevel.READ_ONLY,
            input_schema="SearchRequest",
            output_schema="SearchResponse",
        ),
        _capability(
            "sdk.process",
            "SDK process call",
            surface=SurfaceKind.SDK,
            owner_module="nlp_policy_nz.client.sync",
            description="Typed client method for pipeline processing.",
            side_effect=SideEffectLevel.LOCAL_WRITE,
            input_schema="ProcessRequest",
            output_schema="ProcessResponse",
        ),
        _capability(
            "report.multi_engine_parity",
            "Multi-engine parity report",
            surface=SurfaceKind.REPORT,
            owner_module="nlp_policy_nz.ontology.multi_engine_parity",
            description="Deterministic PolicyEngine/OpenFisca parity evidence bundle.",
            side_effect=SideEffectLevel.LOCAL_WRITE,
            legal_review_boundary=True,
            input_schema="MultiEngineParityBundle",
            output_schema="MultiEngineParityReport",
        ),
        _capability(
            "report.rulespec_promotion",
            "RuleSpec promotion report",
            surface=SurfaceKind.REPORT,
            owner_module="nlp_policy_nz.rulespec_promotion",
            description="Candidate promotion report for rules-as-code handoff.",
            side_effect=SideEffectLevel.READ_ONLY,
            legal_review_boundary=True,
            input_schema="RulesSpecPromotionReport",
            output_schema="RulesSpecPromotionReport",
        ),
        _capability(
            "mcp.search",
            "MCP search tool",
            surface=SurfaceKind.MCP,
            owner_module="nlp_policy_nz.mcp.server",
            description="Read-only MCP search over local corpus outputs.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            experimental=True,
        ),
        _capability(
            "mcp.provenance",
            "MCP provenance tool",
            surface=SurfaceKind.MCP,
            owner_module="nlp_policy_nz.mcp.server",
            description="Read-only MCP access to provenance and report metadata.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            experimental=True,
        ),
        _capability(
            "mcp.quality_report",
            "MCP quality report tool",
            surface=SurfaceKind.MCP,
            owner_module="nlp_policy_nz.mcp.server",
            description="Read-only access to the latest quality reports and summaries.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            experimental=True,
        ),
        _capability(
            "mcp.ontology_summary",
            "MCP ontology summary tool",
            surface=SurfaceKind.MCP,
            owner_module="nlp_policy_nz.mcp.server",
            description="Read-only access to ontology and vocabulary summaries.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            experimental=True,
        ),
        _capability(
            "mcp.rac_candidates",
            "MCP rules-as-code candidate tool",
            surface=SurfaceKind.MCP,
            owner_module="nlp_policy_nz.mcp.server",
            description="Read-only inspection of rules-as-code candidate artifacts.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            experimental=True,
        ),
        _capability(
            "mcp.multi_engine_parity",
            "MCP parity report tool",
            surface=SurfaceKind.MCP,
            owner_module="nlp_policy_nz.mcp.server",
            description="Read-only inspection of multi-engine parity reports.",
            side_effect=SideEffectLevel.READ_ONLY,
            auth_requirement=AuthRequirement.OPTIONAL,
            auth_scope="read",
            experimental=True,
        ),
    ),
)


def load_interface_contract_json(path: str | Path) -> InterfaceContract:
    """Load a contract from JSON on disk."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = tuple(
        CapabilityRecord(
            capability_id=str(item["capability_id"]),
            title=str(item["title"]),
            surface=SurfaceKind(str(item["surface"])),
            owner_module=str(item["owner_module"]),
            description=str(item["description"]),
            side_effect=SideEffectLevel(str(item["side_effect"])),
            auth_requirement=AuthRequirement(str(item.get("auth_requirement", "none"))),
            auth_scope=item.get("auth_scope"),
            legal_review_boundary=bool(item.get("legal_review_boundary", False)),
            github_actions_safe=bool(item.get("github_actions_safe", True)),
            input_schema=item.get("input_schema"),
            output_schema=item.get("output_schema"),
            version=str(item.get("version", "v1")),
            experimental=bool(item.get("experimental", False)),
        )
        for item in payload["capabilities"]
    )
    contract = InterfaceContract(
        contract_id=str(payload["contract_id"]),
        contract_version=str(payload["contract_version"]),
        generated_from=str(payload["generated_from"]),
        capabilities=records,
    )
    contract.validate()
    return contract


def write_interface_contract_json(
    contract: InterfaceContract,
    path: str | Path,
) -> Path:
    """Write a contract JSON artifact to disk."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(contract.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def capability_inventory(contract: InterfaceContract = DEFAULT_INTERFACE_CONTRACT) -> list[dict[str, Any]]:
    """Return a serialisable capability inventory for docs or checks."""
    return [record.to_dict() for record in contract.capabilities]


def surface_inventory(contract: InterfaceContract = DEFAULT_INTERFACE_CONTRACT) -> dict[str, list[str]]:
    """Return capability IDs grouped by surface."""
    grouped: dict[str, list[str]] = {surface.value: [] for surface in SurfaceKind}
    for record in contract.capabilities:
        grouped[record.surface.value].append(record.capability_id)
    return {surface: sorted(ids) for surface, ids in grouped.items() if ids}


def contract_summary(contract: InterfaceContract = DEFAULT_INTERFACE_CONTRACT) -> dict[str, Any]:
    """Return a compact summary for docs and drift checks."""
    contract.validate()
    return {
        "contract_id": contract.contract_id,
        "contract_version": contract.contract_version,
        "generated_from": contract.generated_from,
        "capability_count": len(contract.capabilities),
        "surfaces": surface_inventory(contract),
    }


__all__ = [
    "AuthRequirement",
    "CapabilityRecord",
    "DEFAULT_INTERFACE_CONTRACT",
    "InterfaceContract",
    "SideEffectLevel",
    "SurfaceKind",
    "capability_inventory",
    "contract_summary",
    "load_interface_contract_json",
    "surface_inventory",
    "write_interface_contract_json",
]
