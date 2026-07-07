"""Cross-surface contract governance helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nlp_policy_nz.capabilities import DEFAULT_CAPABILITY_REGISTRY, CapabilitySurface
from nlp_policy_nz.interface_contract import DEFAULT_INTERFACE_CONTRACT, surface_inventory

SURFACE_ORDER: tuple[str, ...] = ("cli", "api", "sdk", "report", "mcp")


@dataclass(frozen=True, slots=True)
class ConformanceRow:
    """A single cross-surface conformance record."""

    surface: str
    interface_contract_ids: tuple[str, ...]
    registry_ids: tuple[str, ...]
    interface_contract_count: int
    registry_count: int
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "surface": self.surface,
            "interface_contract_ids": list(self.interface_contract_ids),
            "registry_ids": list(self.registry_ids),
            "interface_contract_count": self.interface_contract_count,
            "registry_count": self.registry_count,
            "status": self.status,
        }


def _registry_ids_for_surface(surface: str) -> tuple[str, ...]:
    if surface == "report":
        return ()
    return tuple(entry.id for entry in DEFAULT_CAPABILITY_REGISTRY.by_surface(CapabilitySurface(surface)))


def build_conformance_matrix() -> tuple[ConformanceRow, ...]:
    """Build a cross-surface conformance matrix."""
    contract_inventory = surface_inventory(DEFAULT_INTERFACE_CONTRACT)
    rows = []
    for surface in SURFACE_ORDER:
        interface_ids = tuple(contract_inventory.get(surface, ()))
        registry_ids = _registry_ids_for_surface(surface)
        if interface_ids and registry_ids:
            status = "aligned"
        elif interface_ids:
            status = "interface_only"
        elif registry_ids:
            status = "registry_only"
        else:
            status = "missing"
        rows.append(
            ConformanceRow(
                surface=surface,
                interface_contract_ids=interface_ids,
                registry_ids=registry_ids,
                interface_contract_count=len(interface_ids),
                registry_count=len(registry_ids),
                status=status,
            )
        )
    return tuple(rows)


def detect_surface_gaps(matrix: tuple[ConformanceRow, ...] | None = None) -> list[dict[str, Any]]:
    """Return the surfaces that are only represented on one side of the contract."""
    rows = matrix or build_conformance_matrix()
    gaps = []
    for row in rows:
        if row.status == "aligned":
            continue
        gaps.append(
            {
                "surface": row.surface,
                "status": row.status,
                "interface_contract_count": row.interface_contract_count,
                "registry_count": row.registry_count,
            }
        )
    return gaps


def release_checklist() -> tuple[str, ...]:
    """Return the release checklist items for contract governance."""
    return (
        "Refresh the CLI, API, SDK, and MCP contract artifacts.",
        "Regenerate OpenAPI and surface inventory fixtures.",
        "Run contract, CLI, API, MCP, and governance tests.",
        "Verify GitHub issue mirror and project fields remain synchronized.",
        "Record any intentional gaps as roadmap items before release.",
    )


def build_contract_governance_report() -> dict[str, Any]:
    """Build a JSON-ready governance report."""
    matrix = build_conformance_matrix()
    return {
        "surface_count": len(matrix),
        "matrix": [row.to_dict() for row in matrix],
        "gaps": detect_surface_gaps(matrix),
        "release_checklist": list(release_checklist()),
        "interface_contract": DEFAULT_INTERFACE_CONTRACT.to_dict(),
        "capability_registry": DEFAULT_CAPABILITY_REGISTRY.to_dict(),
    }


def write_contract_governance_artifacts(output_dir: str | Path) -> dict[str, Path]:
    """Write JSON and Markdown governance artifacts to disk."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    report = build_contract_governance_report()
    json_path = root / "contract_governance.json"
    markdown_path = root / "contract_governance.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_lines = [
        "# Contract Governance",
        "",
        "| Surface | Interface Contract | Registry | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["matrix"]:
        markdown_lines.append(
            f"| {row['surface']} | {row['interface_contract_count']} | {row['registry_count']} | {row['status']} |"
        )
    markdown_lines.append("")
    markdown_lines.append("## Release Checklist")
    markdown_lines.append("")
    for item in report["release_checklist"]:
        markdown_lines.append(f"- {item}")
    markdown_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    return {
        "contract_governance.json": json_path,
        "contract_governance.md": markdown_path,
    }


__all__ = [
    "ConformanceRow",
    "build_conformance_matrix",
    "build_contract_governance_report",
    "detect_surface_gaps",
    "release_checklist",
    "write_contract_governance_artifacts",
]
