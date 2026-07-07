"""Cross-surface contract tests for the public CLI, API, and MCP adapters."""

from __future__ import annotations

from nlp_policy_nz.api.server import ENDPOINT_INVENTORY, api_contract_summary, api_endpoint_inventory
from nlp_policy_nz.cli.main import CLI_CAPABILITIES, CLI_CAPABILITY_BY_COMMAND, cli_contract_summary
from nlp_policy_nz.mcp.server import build_mcp_manifest, build_mcp_tool_inventory


def test_cli_contract_summary_matches_registry() -> None:
    summary = cli_contract_summary()

    assert summary["capability_count"] == len(CLI_CAPABILITIES)
    assert ["process"] in summary["commands"]
    assert ["completion", "manpage"] in summary["commands"]
    assert CLI_CAPABILITY_BY_COMMAND[("search",)].capability_id == "track81.cli.search"


def test_api_contract_summary_matches_endpoint_inventory() -> None:
    summary = api_contract_summary()
    inventory = api_endpoint_inventory()

    assert summary["endpoint_count"] == len(ENDPOINT_INVENTORY)
    assert any(item["path"] == "/health" for item in inventory)
    assert any(item["path"] == "/process" for item in inventory)
    assert summary["scoped_paths"]["/process"] == "write"


def test_mcp_manifest_is_read_only_and_inventory_backed() -> None:
    manifest = build_mcp_manifest()
    tools = build_mcp_tool_inventory()

    assert manifest["read_only"] is True
    assert manifest["tool_count"] == len(tools)
    assert {tool["name"] for tool in tools} == {
        "search_catalog",
        "inspect_provenance",
        "inspect_quality_report",
        "summarize_ontology",
        "summarize_knowledge_graph",
        "inspect_rules_as_code_candidates",
        "inspect_multi_engine_parity",
    }
