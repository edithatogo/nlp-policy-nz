"""Tests for Track 85 cross-surface contract governance."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.governance.interface_contract import (
    build_interface_surface_conformance_report,
    render_interface_surface_conformance_json,
    render_interface_surface_conformance_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "track81" / "interface_surface_registry.json"


def test_track85_registry_and_docs_are_linked() -> None:
    """The registry snapshot should carry the governance docs references."""
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "track81.interface-surface-registry.v1"
    assert payload["registry_id"] == "track81.interface-surface-registry"
    assert "docs/interface-contract-governance.md" in payload["documentation"]
    assert payload["capabilities"][0]["capability_id"] == "nlp.process"
    assert payload["capabilities"][-1]["capability_id"] == "nlp.tooling"


def test_track85_conformance_report_passes_for_current_repo() -> None:
    """The live CLI, API, and SDK surfaces should match the registry snapshot."""
    report = build_interface_surface_conformance_report(REGISTRY)

    assert report["passed"] is True
    assert report["status"] == "pass"
    assert report["surface_checks"]["cli"]["missing"] == []
    assert report["surface_checks"]["api"]["missing"] == []
    assert report["surface_checks"]["sdk"]["missing"] == []
    assert report["adapter_gap_report"]["missing_core_functions"] == []
    assert report["summary"]["planned_mcp_capabilities"] == 0


def test_track85_conformance_report_renders_deterministically() -> None:
    """The JSON and Markdown renderers should stay stable for GitHub Actions."""
    report = build_interface_surface_conformance_report(REGISTRY)

    rendered_json = render_interface_surface_conformance_json(report)
    rendered_markdown = render_interface_surface_conformance_markdown(report)

    assert json.loads(rendered_json)["schema_version"] == "track85.cross-surface-conformance.v1"
    assert "# Cross-Surface Conformance Report" in rendered_markdown
    assert "| cli |" in rendered_markdown
    assert "planned MCP" in rendered_markdown
