"""Read-only MCP adapter surface for local agent consumption.

The module keeps the adapter thin by delegating all substantive work to the
existing core helpers. The checked-in interface contract is the source of
truth for capability IDs and side-effect classification.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final

from nlp_policy_nz.capabilities import (
    CapabilityEntry,
    DEFAULT_CAPABILITY_REGISTRY,
)
from nlp_policy_nz.interface_contract import (
    DEFAULT_INTERFACE_CONTRACT,
    AuthRequirement,
    CapabilityRecord,
    SideEffectLevel,
)
from nlp_policy_nz.extraction.rules_as_code import (
    build_rules_as_code_candidate_bundle_from_source_inventory,
)
from nlp_policy_nz.extraction.schemas import render_extraction_manifest_json
from nlp_policy_nz.ontology import (
    build_multi_engine_parity_bundle,
    build_nz_ontology_bundle,
    build_nz_ontology_graph,
    build_ontology_standards_manifest,
    load_track80_domain_json,
)
from nlp_policy_nz.provenance import load_provenance_sidecar, provenance_sidecar_path
from nlp_policy_nz.quality.monitoring import load_quality_report
from nlp_policy_nz.quality.track25_ontology_coverage import build_track25_ontology_coverage_audit

MCP_SERVER_NAME: Final[str] = "nlp-policy-nz"
MCP_SERVER_VERSION: Final[str] = "0.1.0"
TRACK81_CONTRACT_ID: Final[str] = DEFAULT_INTERFACE_CONTRACT.contract_id
TRACK81_CONTRACT_VERSION: Final[str] = DEFAULT_INTERFACE_CONTRACT.contract_version

_TRACK81_CAPABILITY_INDEX: Final[dict[str, CapabilityRecord]] = {
    record.capability_id: record for record in DEFAULT_INTERFACE_CONTRACT.capabilities
}
_CORE_CAPABILITY_INDEX: Final[dict[str, CapabilityEntry]] = {
    entry.id: entry for entry in DEFAULT_CAPABILITY_REGISTRY.entries
}


class MCPDependencyError(RuntimeError):
    """Raised when the optional MCP SDK is unavailable."""


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """JSON-serialisable description of one read-only MCP tool."""

    name: str
    title: str
    description: str
    capability_ids: tuple[str, ...]
    owner_module: str
    side_effect: SideEffectLevel
    auth_requirement: AuthRequirement
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "capability_ids": list(self.capability_ids),
            "owner_module": self.owner_module,
            "side_effect": self.side_effect.value,
            "auth_requirement": self.auth_requirement.value,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }


@dataclass(frozen=True, slots=True)
class ResourceSpec:
    """JSON-serialisable description of one read-only MCP resource."""

    name: str
    uri: str
    title: str
    description: str
    capability_ids: tuple[str, ...]
    owner_module: str
    side_effect: SideEffectLevel
    auth_requirement: AuthRequirement
    content_type: str
    schema: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "uri": self.uri,
            "title": self.title,
            "description": self.description,
            "capability_ids": list(self.capability_ids),
            "owner_module": self.owner_module,
            "side_effect": self.side_effect.value,
            "auth_requirement": self.auth_requirement.value,
            "content_type": self.content_type,
            "schema": self.schema,
        }


_TOOL_SPECS: Final[tuple[ToolSpec, ...]] = (
    ToolSpec(
        name="search_catalog",
        title="Search catalog",
        description="Search the Track 81 contract and MCP surface metadata.",
        capability_ids=("cli.search", "api.search", "sdk.search-similar"),
        owner_module="nlp_policy_nz.mcp.server",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1},
                "limit": {"type": "integer", "minimum": 1, "maximum": 25, "default": 5},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "matches": {"type": "array"},
                "sources": {"type": "array"},
            },
            "required": ["query", "matches", "sources"],
        },
    ),
    ToolSpec(
        name="inspect_provenance",
        title="Inspect provenance",
        description="Load a PROV-O sidecar or report and return a compact summary.",
        capability_ids=("cli.provenance",),
        owner_module="nlp_policy_nz.provenance.recorder",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "minLength": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        output_schema={"type": "object"},
    ),
    ToolSpec(
        name="inspect_quality_report",
        title="Inspect quality report",
        description="Load a persisted quality report and expose the summary fields.",
        capability_ids=("cli.quality.report",),
        owner_module="nlp_policy_nz.quality.monitoring",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "minLength": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        output_schema={"type": "object"},
    ),
    ToolSpec(
        name="summarize_ontology",
        title="Summarize ontology coverage",
        description="Summarize the checked-in ontology coverage and standards manifests.",
        capability_ids=("cli.export-nz-ontologies",),
        owner_module="nlp_policy_nz.quality.track25_ontology_coverage",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "repo_root": {"type": "string"},
            },
            "additionalProperties": False,
        },
        output_schema={"type": "object"},
    ),
    ToolSpec(
        name="summarize_knowledge_graph",
        title="Summarize knowledge graph",
        description="Summarize the checked-in NZ ontology bundle and RDF graph.",
        capability_ids=("cli.knowledge-graph", "cli.export-rdf"),
        owner_module="nlp_policy_nz.ontology.nz_ontologies",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "repo_root": {"type": "string"},
            },
            "additionalProperties": False,
        },
        output_schema={"type": "object"},
    ),
    ToolSpec(
        name="inspect_rules_as_code_candidates",
        title="Inspect rules-as-code candidates",
        description="Inspect the deterministic Track 77 candidate bundle.",
        capability_ids=("cli.export-rac-candidates",),
        owner_module="nlp_policy_nz.extraction.rules_as_code",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "enum": ["inventory"],
                    "default": "inventory",
                },
            },
            "additionalProperties": False,
        },
        output_schema={"type": "object"},
    ),
    ToolSpec(
        name="inspect_multi_engine_parity",
        title="Inspect multi-engine parity",
        description="Inspect the Track 80 parity bundle and report.",
        capability_ids=("cli.multi-engine-parity",),
        owner_module="nlp_policy_nz.ontology.multi_engine_parity",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        input_schema={
            "type": "object",
            "properties": {
                "manifest_path": {"type": "string"},
            },
            "additionalProperties": False,
        },
        output_schema={"type": "object"},
    ),
)

_RESOURCE_SPECS: Final[tuple[ResourceSpec, ...]] = (
    ResourceSpec(
        name="capability_registry",
        uri=f"{MCP_SERVER_NAME}://track81/capability-registry",
        title="Capability registry",
        description="Machine-readable Track 81 capability and adapter registry.",
        capability_ids=("mcp.registry.list",),
        owner_module="nlp_policy_nz.interface_contract",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        content_type="application/json",
        schema={"type": "object"},
    ),
    ResourceSpec(
        name="tool_schemas",
        uri=f"{MCP_SERVER_NAME}://track84/tool-schemas",
        title="Tool schemas",
        description="JSON schemas for the read-only MCP tool surface.",
        capability_ids=("mcp.registry.list",),
        owner_module="nlp_policy_nz.mcp.server",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        content_type="application/json",
        schema={"type": "object"},
    ),
    ResourceSpec(
        name="resource_schemas",
        uri=f"{MCP_SERVER_NAME}://track84/resource-schemas",
        title="Resource schemas",
        description="JSON schemas for the read-only MCP resource surface.",
        capability_ids=("mcp.registry.list",),
        owner_module="nlp_policy_nz.mcp.server",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        content_type="application/json",
        schema={"type": "object"},
    ),
    ResourceSpec(
        name="generated_docs",
        uri=f"{MCP_SERVER_NAME}://track84/generated-docs",
        title="Generated docs",
        description="Markdown guidance for the MCP adapter and its safety boundaries.",
        capability_ids=("mcp.registry.list",),
        owner_module="nlp_policy_nz.mcp.server",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        content_type="text/markdown",
        schema={"type": "string"},
    ),
    ResourceSpec(
        name="track81_status",
        uri=f"{MCP_SERVER_NAME}://track81/status",
        title="Track 81 status",
        description="Selected Track 81 conductor artifacts and contract metadata.",
        capability_ids=("mcp.registry.list",),
        owner_module="nlp_policy_nz.mcp.server",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        content_type="application/json",
        schema={"type": "object"},
    ),
    ResourceSpec(
        name="track84_status",
        uri=f"{MCP_SERVER_NAME}://track84/status",
        title="Track 84 status",
        description="Selected Track 84 conductor artifacts and implementation metadata.",
        capability_ids=("mcp.registry.list",),
        owner_module="nlp_policy_nz.mcp.server",
        side_effect=SideEffectLevel.READ_ONLY,
        auth_requirement=AuthRequirement.NONE,
        content_type="application/json",
        schema={"type": "object"},
    ),
)


def build_mcp_manifest(*, repo_root: Path | str | None = None) -> dict[str, Any]:
    """Return the machine-readable MCP surface manifest."""

    root = _repo_root(repo_root)
    track81_artifacts = _track_artifact_bundle(root, "track81_interface_surface_contract_20260706")
    track84_artifacts = _track_artifact_bundle(root, "track84_mcp_server_surface_20260706")
    return {
        "server_name": MCP_SERVER_NAME,
        "server_version": MCP_SERVER_VERSION,
        "contract_id": TRACK81_CONTRACT_ID,
        "contract_version": TRACK81_CONTRACT_VERSION,
        "interface_contract": DEFAULT_INTERFACE_CONTRACT.to_dict(),
        "capability_registry": _capability_registry_payload(),
        "tools": [spec.to_dict() for spec in _TOOL_SPECS],
        "resources": [spec.to_dict() for spec in _RESOURCE_SPECS],
        "docs_index": _docs_index(root),
        "read_only": True,
        "optional_dependency": "mcp",
        "tool_count": len(_TOOL_SPECS),
        "track_artifacts": {
            "track81": track81_artifacts,
            "track84": track84_artifacts,
        },
        "schemas": {
            "tools": _tool_schema_catalog(),
            "resources": _resource_schema_catalog(),
        },
    }


def build_mcp_tool_inventory() -> tuple[dict[str, Any], ...]:
    """Return the read-only MCP tool inventory."""

    return tuple(spec.to_dict() for spec in _TOOL_SPECS)


def call_tool(name: str, /, **arguments: Any) -> dict[str, Any]:
    """Invoke one read-only MCP tool against the core helpers."""

    dispatch: dict[str, Callable[..., dict[str, Any]]] = {
        "search_catalog": _search_catalog,
        "inspect_provenance": _inspect_provenance,
        "inspect_quality_report": _inspect_quality_report,
        "summarize_ontology": _summarize_ontology,
        "summarize_knowledge_graph": _summarize_knowledge_graph,
        "inspect_rules_as_code_candidates": _inspect_rules_as_code_candidates,
        "inspect_multi_engine_parity": _inspect_multi_engine_parity,
    }
    try:
        handler = dispatch[name]
    except KeyError as exc:
        msg = f"Unknown MCP tool: {name}"
        raise KeyError(msg) from exc
    return handler(**arguments)


def read_resource(name: str, /, **arguments: Any) -> dict[str, Any]:
    """Return the payload for one read-only MCP resource."""

    dispatch: dict[str, Callable[..., dict[str, Any]]] = {
        "capability_registry": _resource_capability_registry,
        "tool_schemas": _resource_tool_schemas,
        "resource_schemas": _resource_resource_schemas,
        "generated_docs": _resource_generated_docs,
        "track81_status": _resource_track81_status,
        "track84_status": _resource_track84_status,
    }
    try:
        handler = dispatch[name]
    except KeyError as exc:
        msg = f"Unknown MCP resource: {name}"
        raise KeyError(msg) from exc
    return handler(**arguments)


def build_fastmcp_server() -> Any:
    """Build a FastMCP server if the optional SDK dependency is installed."""

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - exercised only when extra is absent
        raise MCPDependencyError(
            "Install the optional 'mcp' extra to run the live MCP server."
        ) from exc

    server = FastMCP(MCP_SERVER_NAME)
    _register_fastmcp_tools(server)
    _register_fastmcp_resources(server)
    return server


def main(argv: list[str] | None = None) -> int:
    """Entry point for the optional MCP stdio server."""

    parser = argparse.ArgumentParser(prog="nlp-policy-nz-mcp")
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Print the JSON surface manifest and exit.",
    )
    args = parser.parse_args(argv)

    if args.manifest:
        print(json.dumps(build_mcp_manifest(), indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    try:
        server = build_fastmcp_server()
    except MCPDependencyError:
        print(
            json.dumps(
                {
                    "error": "Optional MCP dependency is not installed.",
                    "install": "pip install 'nlp-policy-nz[mcp]'",
                    "manifest": build_mcp_manifest(),
                },
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1

    server.run(transport="stdio")
    return 0


def _register_fastmcp_tools(server: Any) -> None:
    """Register the tool handlers with an optional FastMCP instance."""

    @server.tool(name="search_catalog", description=_TOOL_SPECS[0].description)
    def search_catalog(query: str, limit: int = 5) -> dict[str, Any]:
        return _search_catalog(query=query, limit=limit)

    @server.tool(name="inspect_provenance", description=_TOOL_SPECS[1].description)
    def inspect_provenance(path: str) -> dict[str, Any]:
        return _inspect_provenance(path=path)

    @server.tool(name="inspect_quality_report", description=_TOOL_SPECS[2].description)
    def inspect_quality_report(path: str) -> dict[str, Any]:
        return _inspect_quality_report(path=path)

    @server.tool(name="summarize_ontology", description=_TOOL_SPECS[3].description)
    def summarize_ontology(repo_root: str | None = None) -> dict[str, Any]:
        return _summarize_ontology(repo_root=repo_root)

    @server.tool(name="summarize_knowledge_graph", description=_TOOL_SPECS[4].description)
    def summarize_knowledge_graph(repo_root: str | None = None) -> dict[str, Any]:
        return _summarize_knowledge_graph(repo_root=repo_root)

    @server.tool(
        name="inspect_rules_as_code_candidates",
        description=_TOOL_SPECS[5].description,
    )
    def inspect_rules_as_code_candidates(source: str = "inventory") -> dict[str, Any]:
        return _inspect_rules_as_code_candidates(source=source)

    @server.tool(
        name="inspect_multi_engine_parity",
        description=_TOOL_SPECS[6].description,
    )
    def inspect_multi_engine_parity(manifest_path: str | None = None) -> dict[str, Any]:
        return _inspect_multi_engine_parity(manifest_path=manifest_path)


def _register_fastmcp_resources(server: Any) -> None:
    """Register the resource handlers with an optional FastMCP instance."""

    @server.resource("nlp-policy-nz://track81/capability-registry")
    def capability_registry() -> dict[str, Any]:
        return _resource_capability_registry()

    @server.resource("nlp-policy-nz://track84/tool-schemas")
    def tool_schemas() -> dict[str, Any]:
        return _resource_tool_schemas()

    @server.resource("nlp-policy-nz://track84/resource-schemas")
    def resource_schemas() -> dict[str, Any]:
        return _resource_resource_schemas()

    @server.resource("nlp-policy-nz://track84/generated-docs")
    def generated_docs() -> str:
        return _resource_generated_docs()["markdown"]

    @server.resource("nlp-policy-nz://track81/status")
    def track81_status() -> dict[str, Any]:
        return _resource_track81_status()

    @server.resource("nlp-policy-nz://track84/status")
    def track84_status() -> dict[str, Any]:
        return _resource_track84_status()


def _search_catalog(*, query: str, limit: int = 5) -> dict[str, Any]:
    query = query.strip()
    if not query:
        raise ValueError("query is required")
    limit = max(1, min(25, int(limit)))
    terms = [term for term in query.casefold().split() if term]
    matches: list[dict[str, Any]] = []
    for entry in _search_entries():
        score, fields = _score_entry(entry, terms)
        if score <= 0:
            continue
        matches.append(
            {
                "type": entry["type"],
                "id": entry["id"],
                "title": entry["title"],
                "score": round(score, 3),
                "matched_fields": sorted(fields),
                "summary": entry["summary"],
            }
        )
    matches.sort(key=lambda item: (-item["score"], item["type"], item["id"]))
    return {
        "query": query,
        "limit": limit,
        "matches": matches[:limit],
        "sources": sorted({entry["source"] for entry in _search_entries()}),
    }


def _inspect_provenance(*, path: str) -> dict[str, Any]:
    candidate = Path(path)
    if candidate.suffix == ".json":
        sidecar = candidate
    else:
        sidecar = provenance_sidecar_path(candidate)
    payload = load_provenance_sidecar(sidecar if sidecar.exists() else candidate)
    return {
        "path": str(candidate.resolve()),
        "sidecar_path": str(sidecar.resolve()),
        "summary": {
            "type": payload.get("@type"),
            "graph_size": len(payload.get("@graph", []))
            if isinstance(payload.get("@graph"), list)
            else 0,
        },
        "payload": payload,
    }


def _inspect_quality_report(*, path: str) -> dict[str, Any]:
    report = load_quality_report(path)
    return {
        "path": str(Path(path).resolve()),
        "summary": report.summary,
        "alerts": list(report.alerts),
        "report": report.to_dict(),
    }


def _summarize_ontology(*, repo_root: str | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    coverage = build_track25_ontology_coverage_audit(root)
    standards = build_ontology_standards_manifest(root)
    return {
        "repo_root": str(root),
        "track25": coverage["summary"],
        "track25_blockers": len(coverage["blocker_register"]),
        "track26": standards["summary"],
        "standard_ids": standards["standard_ids"],
    }


def _summarize_knowledge_graph(*, repo_root: str | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    bundle = build_nz_ontology_bundle()
    graph = build_nz_ontology_graph(bundle)
    return {
        "repo_root": str(root),
        "track31": bundle.summary,
        "graph": {
            "triple_count": len(graph),
        },
        "controlled_vocabularies": [scheme.scheme_id for scheme in bundle.controlled_vocabularies],
    }


def _inspect_rules_as_code_candidates(*, source: str = "inventory") -> dict[str, Any]:
    if source != "inventory":
        raise ValueError("Only the fixture-bounded source inventory is supported.")
    bundle = build_rules_as_code_candidate_bundle_from_source_inventory()
    return {
        "source": source,
        "manifest": json.loads(render_extraction_manifest_json(bundle.manifest)),
        "bridge_records": [record.to_jsonld() for record in bundle.bridge_records],
        "summary": {
            "record_count": bundle.manifest.summary.total_records,
            "known_gap_count": len(bundle.manifest.summary.known_gaps),
        },
    }


def _inspect_multi_engine_parity(*, manifest_path: str | None = None) -> dict[str, Any]:
    domain = (
        load_track80_domain_json(manifest_path)
        if manifest_path is not None
        else load_track80_domain_json()
    )
    bundle = build_multi_engine_parity_bundle(domain)
    return {
        "manifest_path": str(Path(manifest_path).resolve()) if manifest_path else None,
        "bundle": bundle.to_dict(),
        "report": bundle.report.to_dict(),
    }


def _resource_capability_registry() -> dict[str, Any]:
    return {
        "contract": DEFAULT_INTERFACE_CONTRACT.to_dict(),
        "capabilities": [record.to_dict() for record in DEFAULT_INTERFACE_CONTRACT.capabilities],
        "track81_capability_ids": list(_TRACK81_CAPABILITY_INDEX),
    }


def _resource_tool_schemas() -> dict[str, Any]:
    return {
        "tools": [spec.to_dict() for spec in _TOOL_SPECS],
        "by_name": {spec.name: spec.to_dict() for spec in _TOOL_SPECS},
    }


def _resource_resource_schemas() -> dict[str, Any]:
    return {
        "resources": [spec.to_dict() for spec in _RESOURCE_SPECS],
        "by_name": {spec.name: spec.to_dict() for spec in _RESOURCE_SPECS},
    }


def _resource_generated_docs() -> dict[str, Any]:
    return {
        "markdown": _docs_markdown(),
        "summary": {
            "tool_count": len(_TOOL_SPECS),
            "resource_count": len(_RESOURCE_SPECS),
        },
    }


def _resource_track81_status() -> dict[str, Any]:
    return _track_artifact_bundle(_repo_root(None), "track81_interface_surface_contract_20260706")


def _resource_track84_status() -> dict[str, Any]:
    return _track_artifact_bundle(_repo_root(None), "track84_mcp_server_surface_20260706")


def _tool_schema_catalog() -> dict[str, Any]:
    return {spec.name: spec.input_schema for spec in _TOOL_SPECS}


def _resource_schema_catalog() -> dict[str, Any]:
    return {spec.name: spec.schema for spec in _RESOURCE_SPECS}


def _capability_registry_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "source": "nlp_policy_nz.interface_contract",
        "entry_count": len(DEFAULT_INTERFACE_CONTRACT.capabilities),
        "entries": [record.to_dict() for record in DEFAULT_INTERFACE_CONTRACT.capabilities],
    }


def _track_artifact_bundle(root: Path, track_dir_name: str) -> dict[str, Any]:
    candidate_dirs = (
        root / "conductor" / "tracks" / track_dir_name,
        root / "conductor" / "tracks" / "archive" / track_dir_name,
        root / "conductor" / "archive" / track_dir_name,
    )
    track_dir = next((path for path in candidate_dirs if path.exists()), candidate_dirs[-1])
    files = ("index.md", "metadata.json", "plan.md", "spec.md", "evidence.md")
    artifacts: dict[str, str] = {}
    for filename in files:
        path = track_dir / filename
        if path.is_file():
            artifacts[filename] = path.read_text(encoding="utf-8")
    return {
        "track_dir": str(track_dir),
        "files": artifacts,
    }


def _docs_index(root: Path) -> dict[str, Any]:
    return {
        "capabilities": [
            {
                "capability_id": record.capability_id,
                "title": record.title,
                "surface": record.surface.value,
                "side_effect": record.side_effect.value,
                "owner_module": record.owner_module,
            }
            for record in DEFAULT_INTERFACE_CONTRACT.capabilities
        ],
        "docs": {
            "capabilities": str(root / "docs" / "capabilities.md"),
            "interface_contract": str(root / "src" / "nlp_policy_nz" / "interface_contract.py"),
            "mcp_server": str(root / "src" / "nlp_policy_nz" / "mcp" / "server.py"),
        },
    }


def _docs_markdown() -> str:
    return "\n".join(
        [
            "# nlp-policy-nz MCP Adapter",
            "",
            "Read-only tools and resources are thin adapters over the core package.",
            "",
            "## Safety boundaries",
            "",
            "- No mutating, publishing, or external-network tools are registered.",
            "- The optional `mcp` extra is only required to run the stdio server.",
            "- Tool and resource metadata are driven from the Track 81 contract.",
            "",
            "## Registered tools",
            "",
            *[f"- `{spec.name}` -> {', '.join(spec.capability_ids)}" for spec in _TOOL_SPECS],
            "",
            "## Registered resources",
            "",
            *[f"- `{spec.name}` -> {', '.join(spec.capability_ids)}" for spec in _RESOURCE_SPECS],
        ]
    )


def _search_entries() -> tuple[dict[str, Any], ...]:
    entries: list[dict[str, Any]] = []
    for spec in _TOOL_SPECS:
        entries.append(
            {
                "type": "tool",
                "id": spec.name,
                "title": spec.title,
                "summary": spec.description,
                "source": "tool-spec",
                "keywords": " ".join(
                    [
                        spec.name,
                        spec.title,
                        spec.description,
                        " ".join(spec.capability_ids),
                        spec.owner_module,
                    ]
                ),
            }
        )
    for spec in _RESOURCE_SPECS:
        entries.append(
            {
                "type": "resource",
                "id": spec.name,
                "title": spec.title,
                "summary": spec.description,
                "source": "resource-spec",
                "keywords": " ".join(
                    [
                        spec.name,
                        spec.title,
                        spec.description,
                        " ".join(spec.capability_ids),
                        spec.owner_module,
                    ]
                ),
            }
        )
    for record in DEFAULT_INTERFACE_CONTRACT.capabilities:
        entries.append(
            {
                "type": "capability",
                "id": record.capability_id,
                "title": record.title,
                "summary": record.description,
                "source": "interface-contract",
                "keywords": " ".join(
                    [
                        record.capability_id,
                        record.title,
                        record.description,
                        record.owner_module,
                        record.surface.value,
                        record.side_effect.value,
                    ]
                ),
            }
        )
    return tuple(entries)


def _score_entry(entry: dict[str, Any], terms: list[str]) -> tuple[float, set[str]]:
    fields = {
        "id": str(entry["id"]).casefold(),
        "title": str(entry["title"]).casefold(),
        "summary": str(entry["summary"]).casefold(),
        "keywords": str(entry["keywords"]).casefold(),
    }
    matched_fields: set[str] = set()
    score = 0.0
    for term in terms:
        for field_name, value in fields.items():
            if term in value:
                matched_fields.add(field_name)
                score += 1.0 if field_name == "id" else 0.5
    return score, matched_fields


def _repo_root(repo_root: Path | str | None) -> Path:
    if repo_root is not None:
        return Path(repo_root).resolve()
    return Path(__file__).resolve().parents[3]


__all__ = [
    "MCPDependencyError",
    "MCP_SERVER_NAME",
    "MCP_SERVER_VERSION",
    "build_fastmcp_server",
    "build_mcp_manifest",
    "build_mcp_tool_inventory",
    "call_tool",
    "main",
    "read_resource",
]
