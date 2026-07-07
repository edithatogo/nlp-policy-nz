"""Track 85 cross-surface contract registry and conformance checks.

The contract stays intentionally static and deterministic. It loads the checked-in
Track 81 registry snapshot, compares it with the live CLI/API/SDK surface
exposures, and reports planned MCP gaps without treating them as failures.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Final

REGISTRY_SCHEMA_VERSION: Final[str] = "track81.interface-surface-registry.v1"
CONFORMANCE_SCHEMA_VERSION: Final[str] = "track85.cross-surface-conformance.v1"
DEFAULT_REGISTRY_PATH: Final[Path] = (
    Path(__file__).resolve().parents[3] / "data" / "track81" / "interface_surface_registry.json"
)


def repo_root() -> Path:
    """Return the repository root that contains ``data/`` and ``docs/``."""

    return DEFAULT_REGISTRY_PATH.parents[2]


def load_interface_surface_registry(registry_path: str | Path | None = None) -> dict[str, Any]:
    """Load the checked-in Track 81 registry snapshot."""

    path = Path(registry_path) if registry_path is not None else DEFAULT_REGISTRY_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def _dedupe_sorted(values: Iterable[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _is_subparser_action(action: object) -> bool:
    return hasattr(action, "choices") and isinstance(getattr(action, "choices"), dict)


def detect_cli_surface() -> tuple[str, ...]:
    """Return the current CLI command tree as stable ``path`` strings."""

    from nlp_policy_nz.cli.main import _build_parser

    paths: list[str] = []

    def walk(parser: object, prefix: tuple[str, ...] = ()) -> None:
        actions = getattr(parser, "_actions", ())
        for action in actions:
            if not _is_subparser_action(action):
                continue
            choices = getattr(action, "choices", {})
            for name in sorted(choices):
                child = choices[name]
                path = prefix + (name,)
                paths.append(" ".join(path))
                walk(child, path)

    walk(_build_parser())
    return tuple(_dedupe_sorted(paths))


def detect_api_surface() -> tuple[str, ...]:
    """Return the public FastAPI route inventory as ``METHOD /path`` strings."""

    from nlp_policy_nz.api.server import app

    routes: list[str] = []
    ignored_paths = {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if not path or not methods or path in ignored_paths:
            continue
        for method in sorted(m for m in methods if m not in {"HEAD", "OPTIONS"}):
            routes.append(f"{method} {path}")
    return tuple(_dedupe_sorted(routes))


def detect_sdk_surface() -> tuple[str, ...]:
    """Return the public SDK method inventory for sync and async clients."""

    from nlp_policy_nz.client import AsyncNLPPolicyNZClient, NLPPolicyNZClient

    methods: list[str] = []
    for client_type in (NLPPolicyNZClient, AsyncNLPPolicyNZClient):
        for name, value in sorted(client_type.__dict__.items()):
            if name.startswith("_") or not callable(value):
                continue
            if name in {"close", "aclose"}:
                continue
            methods.append(f"{client_type.__name__}.{name}")
    return tuple(_dedupe_sorted(methods))


def detect_mcp_surface() -> tuple[str, ...]:
    """Return the current MCP surface inventory.

    The current adapter exposes a read-only manifest of tools and resources.
    """

    from nlp_policy_nz.mcp.server import build_mcp_manifest

    manifest = build_mcp_manifest(repo_root=repo_root())
    tool_names = [f"tool:{tool['name']}" for tool in manifest.get("tools", [])]
    resource_names = [
        f"resource:{resource['name']}" for resource in manifest.get("resources", [])
    ]
    return tuple(_dedupe_sorted(tool_names + resource_names))


def _surface_identifiers(capability: dict[str, Any], surface: str) -> tuple[str, ...]:
    payload = capability.get("surfaces", {}).get(surface, {})
    identifiers = payload.get("identifiers", ())
    return tuple(str(item) for item in identifiers)


def _surface_status(capability: dict[str, Any], surface: str) -> str:
    payload = capability.get("surfaces", {}).get(surface, {})
    return str(payload.get("status", "not_applicable"))


def _registry_expected_surface(capabilities: Sequence[dict[str, Any]], surface: str) -> tuple[str, ...]:
    expected: list[str] = []
    for capability in capabilities:
        if _surface_status(capability, surface) == "implemented":
            expected.extend(_surface_identifiers(capability, surface))
    return tuple(_dedupe_sorted(expected))


def _registry_planned_surface(capabilities: Sequence[dict[str, Any]], surface: str) -> tuple[str, ...]:
    planned: list[str] = []
    for capability in capabilities:
        if _surface_status(capability, surface) == "planned":
            planned.extend(_surface_identifiers(capability, surface))
    return tuple(_dedupe_sorted(planned))


def _compare_surface(
    *,
    surface_name: str,
    expected: Sequence[str],
    observed: Sequence[str],
) -> dict[str, Any]:
    expected_set = set(expected)
    observed_set = set(observed)
    return {
        "surface": surface_name,
        "expected": list(expected),
        "observed": list(observed),
        "missing": sorted(expected_set - observed_set),
        "extra": sorted(observed_set - expected_set),
        "passed": expected_set == observed_set,
    }


def _verify_core_functions(capabilities: Sequence[dict[str, Any]]) -> tuple[str, ...]:
    missing: list[str] = []
    for capability in capabilities:
        for dotted_name in capability.get("core_functions", ()):
            module_name, _, attr_name = str(dotted_name).rpartition(".")
            if not module_name or not attr_name:
                missing.append(str(dotted_name))
                continue
            try:
                spec = importlib.util.find_spec(module_name)
            except Exception:  # noqa: BLE001
                missing.append(str(dotted_name))
                continue
            if spec is None or spec.origin is None:
                missing.append(str(dotted_name))
                continue
            try:
                origin = Path(spec.origin).resolve()
            except Exception:  # noqa: BLE001
                missing.append(str(dotted_name))
                continue
            search_root = origin.parent if origin.name != "__init__.py" else origin.parent
            symbol_pattern = re.compile(rf"^(?:async\s+def|def|class)\s+{re.escape(attr_name)}\b", re.MULTILINE)
            found = False
            for candidate in sorted(search_root.rglob("*.py")):
                try:
                    source = candidate.read_text(encoding="utf-8")
                except Exception:  # noqa: BLE001
                    continue
                if symbol_pattern.search(source):
                    found = True
                    break
            if not found:
                missing.append(str(dotted_name))
    return tuple(_dedupe_sorted(missing))


def _build_docs_checks(registry: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for rel_path in registry.get("documentation", ()):
        path = repo_root() / Path(rel_path)
        checks.append(
            {
                "path": rel_path,
                "exists": path.is_file(),
            }
        )
    return checks


def build_interface_surface_conformance_report(
    registry_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a deterministic cross-surface conformance report."""

    registry = load_interface_surface_registry(registry_path)
    capabilities = list(registry.get("capabilities", ()))

    cli_expected = _registry_expected_surface(capabilities, "cli")
    api_expected = _registry_expected_surface(capabilities, "api")
    sdk_expected = _registry_expected_surface(capabilities, "sdk")
    mcp_expected = _registry_expected_surface(capabilities, "mcp")
    mcp_planned = _registry_planned_surface(capabilities, "mcp")

    cli_observed = detect_cli_surface()
    api_observed = detect_api_surface()
    sdk_observed = detect_sdk_surface()
    mcp_observed = detect_mcp_surface()

    cli_check = _compare_surface(surface_name="cli", expected=cli_expected, observed=cli_observed)
    api_check = _compare_surface(surface_name="api", expected=api_expected, observed=api_observed)
    sdk_check = _compare_surface(surface_name="sdk", expected=sdk_expected, observed=sdk_observed)
    mcp_check = _compare_surface(surface_name="mcp", expected=mcp_expected, observed=mcp_observed)

    docs_checks = _build_docs_checks(registry)
    missing_docs = [check["path"] for check in docs_checks if not check["exists"]]
    missing_core_functions = _verify_core_functions(capabilities)

    planned_gaps = [
        {
            "capability_id": capability["capability_id"],
            "surface": "mcp",
            "planned_identifiers": list(_surface_identifiers(capability, "mcp")),
        }
        for capability in capabilities
        if _surface_status(capability, "mcp") == "planned"
    ]

    implemented_surface_pass = all(
        check["passed"] for check in (cli_check, api_check, sdk_check)
    )
    docs_pass = not missing_docs
    core_pass = not missing_core_functions

    report = {
        "schema_version": CONFORMANCE_SCHEMA_VERSION,
        "registry_id": registry.get("registry_id"),
        "registry_schema_version": registry.get("schema_version"),
        "surface_checks": {
            "cli": cli_check,
            "api": api_check,
            "sdk": sdk_check,
            "mcp": mcp_check,
        },
        "docs_checks": docs_checks,
        "adapter_gap_report": {
            "missing_core_functions": list(missing_core_functions),
            "planned_mcp_gaps": planned_gaps,
            "surface_orchestration_notes": [
                {
                    "surface": "cli",
                    "module": "src/nlp_policy_nz/cli/main.py",
                    "note": "Command dispatch remains in the CLI adapter; keep it thin and registry-driven.",
                },
                {
                    "surface": "api",
                    "module": "src/nlp_policy_nz/api/server.py",
                    "note": "Versioned HTTP orchestration stays in the API adapter; core pipeline logic belongs below this layer.",
                },
                {
                    "surface": "sdk",
                    "module": "src/nlp_policy_nz/client/sync.py",
                    "note": "Sync and async SDKs share a thin HTTP transport boundary and should remain capability mirrors only.",
                },
                {
                    "surface": "mcp",
                    "module": "planned",
                    "note": "No MCP adapter is implemented yet; Track 84 remains a planned surface.",
                },
            ],
        },
        "status": "pass" if implemented_surface_pass and docs_pass and core_pass else "fail",
        "passed": implemented_surface_pass and docs_pass and core_pass,
        "summary": {
            "implemented_surfaces": {
                "cli": len(cli_expected),
                "api": len(api_expected),
                "sdk": len(sdk_expected),
            },
            "planned_mcp_capabilities": len(mcp_planned),
            "missing_docs": len(missing_docs),
            "missing_core_functions": len(missing_core_functions),
        },
    }
    return report


def render_interface_surface_conformance_json(report: dict[str, Any]) -> str:
    """Render a conformance report as deterministic JSON."""

    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=False)


def render_interface_surface_conformance_markdown(report: dict[str, Any]) -> str:
    """Render a conformance report as a concise Markdown summary."""

    surface_checks = report["surface_checks"]
    docs_checks = report["docs_checks"]
    gaps = report["adapter_gap_report"]
    lines = [
        "# Cross-Surface Conformance Report",
        f"- Registry: `{report['registry_id']}`",
        f"- Schema: `{report['schema_version']}`",
        f"- Status: `{report['status']}`",
        "",
        "## Surface Checks",
        "| surface | expected | observed | missing | extra |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for surface_name in ("cli", "api", "sdk", "mcp"):
        check = surface_checks[surface_name]
        lines.append(
            "| {surface} | {expected} | {observed} | {missing} | {extra} |".format(
                surface=surface_name,
                expected=len(check["expected"]),
                observed=len(check["observed"]),
                missing=len(check["missing"]),
                extra=len(check["extra"]),
            )
        )
    lines.extend(
        [
            "",
            "## Documentation Checks",
        ]
    )
    for item in docs_checks:
        lines.append(f"- `{item['path']}`: {'ok' if item['exists'] else 'missing'}")
    lines.extend(
        [
            "",
            "## Adapter Gaps",
        ]
    )
    missing_core = gaps["missing_core_functions"]
    if missing_core:
        for item in missing_core:
            lines.append(f"- missing core function: `{item}`")
    else:
        lines.append("- missing core function: none")
    if gaps["planned_mcp_gaps"]:
        for item in gaps["planned_mcp_gaps"]:
            planned = ", ".join(item["planned_identifiers"]) or "no identifier yet"
            lines.append(f"- planned MCP: `{item['capability_id']}` -> {planned}")
    else:
        lines.append("- planned MCP: none")
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check-interface-surface-contract",
        description="Validate the Track 81 registry against the live CLI, API, SDK, and MCP surfaces.",
    )
    parser.add_argument(
        "--registry",
        default=str(DEFAULT_REGISTRY_PATH),
        help="Path to the Track 81 interface surface registry JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format for the report.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output file. Defaults to stdout.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint for the conformance check."""

    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    report = build_interface_surface_conformance_report(args.registry)
    rendered = (
        render_interface_surface_conformance_json(report)
        if args.format == "json"
        else render_interface_surface_conformance_markdown(report)
    )
    if args.output is None:
        print(rendered)
    else:
        Path(args.output).write_text(rendered, encoding="utf-8")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
