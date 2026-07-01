"""Generate documentation reference pages from local Python entry points."""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = ROOT / "docs-site" / "src" / "content" / "docs"
NOTEBOOK_ROOT = ROOT / "docs" / "notebooks"

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


def _parser_help() -> str:
    try:
        from nlp_policy_nz.cli.main import _build_parser
    except Exception as exc:  # pragma: no cover - docs-build fallback
        return (
            "nlp-policy-nz [--verbose] <command> [options]\n\n"
            "Live argparse extraction was unavailable during this docs build: "
            f"{exc}\n"
        )

    parser = _build_parser()
    return parser.format_help()


def _openapi_payload() -> dict[str, Any]:
    try:
        from nlp_policy_nz.api.server import app
    except Exception as exc:  # pragma: no cover - docs-build fallback
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "nlp-policy-nz Inference API",
                "version": "0.1.0",
                "description": f"Live OpenAPI extraction unavailable: {exc}",
            },
            "paths": {},
        }

    return app.openapi()


def _python_reference_markdown() -> str:
    modules = (
        "nlp_policy_nz.api.server",
        "nlp_policy_nz.axiom",
        "nlp_policy_nz.extraction",
        "nlp_policy_nz.ontology",
        "nlp_policy_nz.storage",
        "nlp_policy_nz.telemetry",
    )
    lines = [
        "---",
        "title: Python API reference",
        "description: Python module reference generated from public docstrings.",
        "---",
        "",
        "# Python API reference",
        "",
        "This page is generated from module, class, and function docstrings.",
        "",
    ]
    for module_name in modules:
        lines.extend(_module_reference(module_name))
    return "\n".join(lines) + "\n"


def _module_reference(module_name: str) -> list[str]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - docs-build fallback
        return [f"## `{module_name}`", "", f"Import unavailable during docs build: `{exc}`.", ""]
    lines = [f"## `{module_name}`", ""]
    module_doc = inspect.getdoc(module)
    if module_doc:
        lines.extend([module_doc.splitlines()[0], ""])
    public_names = getattr(module, "__all__", None)
    if public_names is None:
        public_names = [
            name
            for name, value in vars(module).items()
            if not name.startswith("_") and (inspect.isclass(value) or inspect.isfunction(value))
        ]
    for name in sorted(public_names):
        value = getattr(module, name, None)
        if value is None or not (inspect.isclass(value) or inspect.isfunction(value)):
            continue
        doc = inspect.getdoc(value)
        if doc:
            lines.append(f"- `{name}`: {doc.splitlines()[0]}")
    lines.append("")
    return lines


def generate_reference_pages(output_root: Path = DOCS_ROOT) -> tuple[Path, ...]:
    """Write OpenAPI, Python API, and CLI reference pages."""
    api_dir = output_root / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    openapi = _openapi_payload()
    openapi_json = api_dir / "openapi.json"
    openapi_json.write_text(json.dumps(openapi, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    openapi_md = api_dir / "openapi.md"
    openapi_md.write_text(
        """---
title: OpenAPI reference
description: FastAPI OpenAPI reference generated from the local app.
---

# OpenAPI reference

The canonical machine-readable OpenAPI document is checked in at
[`openapi.json`](./openapi.json). It is generated from
`nlp_policy_nz.api.server:app` and covers the health, embedding, semantic
search, and processing endpoints.

## Endpoints

"""
        + "\n".join(
            f"- `{method.upper()} {path}`"
            for path, methods in sorted(openapi["paths"].items())
            for method in sorted(methods)
        )
        + "\n",
        encoding="utf-8",
    )
    python_md = api_dir / "python.md"
    python_md.write_text(_python_reference_markdown(), encoding="utf-8")
    cli_md = api_dir / "cli.md"
    cli_md.write_text(
        """---
title: CLI reference
description: Command-line reference generated from argparse help.
---

# CLI reference

```text
"""
        + _parser_help()
        + """```
""",
        encoding="utf-8",
    )
    return openapi_json, openapi_md, python_md, cli_md


def generate_notebook_pages(
    notebook_root: Path = NOTEBOOK_ROOT,
    output_root: Path = DOCS_ROOT,
) -> tuple[Path, ...]:
    """Render lightweight static tutorial pages from notebook markdown cells."""
    tutorials_dir = output_root / "tutorials"
    tutorials_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for notebook_path in sorted(notebook_root.glob("*.ipynb")):
        payload = json.loads(notebook_path.read_text(encoding="utf-8"))
        title = _notebook_title(payload, notebook_path)
        body = _notebook_markdown(payload)
        page = tutorials_dir / f"{notebook_path.stem.replace('_', '-')}.md"
        page.write_text(
            f"""---
title: {title}
description: Static tutorial rendered from {notebook_path.name}.
---

{body}

Source notebook: `docs/notebooks/{notebook_path.name}`.
""",
            encoding="utf-8",
        )
        written.append(page)
    return tuple(written)


def _notebook_title(payload: dict[str, Any], notebook_path: Path) -> str:
    for cell in payload.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        for line in source.splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ").strip()
    return notebook_path.stem.replace("_", " ").title()


def _notebook_markdown(payload: dict[str, Any]) -> str:
    sections: list[str] = []
    for cell in payload.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "markdown":
            sections.append(source)
        elif cell.get("cell_type") == "code":
            sections.append(f"```python\n{source}\n```")
    return "\n\n".join(sections)


def build_parser() -> argparse.ArgumentParser:
    """Return the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DOCS_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Generate reference docs and return a process exit code."""
    args = build_parser().parse_args(argv)
    written = (
        *generate_reference_pages(args.output_root),
        *generate_notebook_pages(output_root=args.output_root),
    )
    for path in written:
        sys.stdout.write(f"{path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
