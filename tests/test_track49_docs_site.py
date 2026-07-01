"""Tests for Track 49 documentation site contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.generate_docs_reference import generate_reference_pages

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs-site" / "src" / "content" / "docs"


def _markdown_pages() -> tuple[Path, ...]:
    return tuple(sorted(DOCS.rglob("*.md")))


def test_track49_docs_site_core_files_exist() -> None:
    required = (
        ROOT / "docs-site" / "astro.config.mjs",
        ROOT / "docs-site" / "package.json",
        ROOT / ".github" / "workflows" / "docs.yml",
        DOCS / "index.md",
        DOCS / "api" / "openapi.md",
        DOCS / "api" / "python.md",
        DOCS / "api" / "cli.md",
        DOCS / "operations" / "runbook.md",
    )

    assert [path for path in required if not path.is_file()] == []


def test_track49_all_required_user_guides_are_present_and_linked() -> None:
    home = (DOCS / "index.md").read_text(encoding="utf-8")
    guide_slugs = (
        "installation",
        "quickstart",
        "guides/ingestion",
        "guides/ontology",
        "guides/search",
        "guides/publishing",
        "guides/client-sdk",
    )

    for slug in guide_slugs:
        assert (DOCS / f"{slug}.md").is_file()
        assert slug.split("/")[-1] in home or slug in home


def test_track49_architecture_runbook_and_versioning_pages_exist() -> None:
    required = (
        "architecture/system-overview.md",
        "architecture/data-flow.md",
        "architecture/ontology-kg.md",
        "architecture/security.md",
        "architecture/adr.md",
        "operations/runbook.md",
        "versioning.md",
    )

    for page in required:
        content = (DOCS / page).read_text(encoding="utf-8")
        assert "# " in content
    assert "flowchart" in (DOCS / "architecture/system-overview.md").read_text(encoding="utf-8")


def test_track49_reference_generator_writes_openapi_python_and_cli_pages(
    tmp_path: Path,
) -> None:
    written = generate_reference_pages(tmp_path)

    assert {path.name for path in written} == {
        "openapi.json",
        "openapi.md",
        "python.md",
        "cli.md",
    }
    assert "paths" in json.loads(tmp_path.joinpath("api/openapi.json").read_text(encoding="utf-8"))
    assert "CLI reference" in tmp_path.joinpath("api/cli.md").read_text(encoding="utf-8")
    python_reference = tmp_path.joinpath("api/python.md").read_text(encoding="utf-8")
    assert "generated from module, class, and function docstrings" in python_reference
    assert "`nlp_policy_nz.api.server`" in python_reference


def test_track49_tutorial_notebooks_are_valid_and_linked() -> None:
    notebooks = tuple(sorted((ROOT / "docs" / "notebooks").glob("*.ipynb")))
    tutorial_pages = tuple(sorted((DOCS / "tutorials").glob("*.md")))

    assert len(notebooks) >= 3
    assert len(tutorial_pages) >= 3
    for notebook in notebooks:
        payload = json.loads(notebook.read_text(encoding="utf-8"))
        assert payload["nbformat"] == 4
        assert payload["cells"]
        rendered_page = DOCS / "tutorials" / f"{notebook.stem.replace('_', '-')}.md"
        rendered = rendered_page.read_text(encoding="utf-8")
        assert notebook.name in rendered
        assert "```python" in rendered
        assert any(notebook.name in page.read_text(encoding="utf-8") for page in tutorial_pages)


def test_track49_docs_workflow_builds_and_deploys_pages() -> None:
    workflow = (ROOT / ".github" / "workflows" / "docs.yml").read_text(encoding="utf-8")

    assert "python scripts/generate_docs_reference.py" in workflow
    assert 'python -m pip install -e ".[dev]"' in workflow
    assert "PYTHONPATH=src python scripts/generate_docs_reference.py" in workflow
    assert "npm run docs:check" in workflow
    assert "npm run docs:build" in workflow
    assert "actions/upload-pages-artifact" in workflow
    assert "actions/deploy-pages" in workflow
    assert "tags: ['v*']" in workflow


def test_track49_internal_markdown_links_resolve() -> None:
    page_paths = {path.relative_to(DOCS).with_suffix("").as_posix() for path in _markdown_pages()}
    page_paths.add("index")
    links = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")

    missing: list[str] = []
    for page in _markdown_pages():
        for match in links.finditer(page.read_text(encoding="utf-8")):
            target = match.group(1).split("#", 1)[0]
            if target.endswith(".json"):
                if not page.parent.joinpath(target).resolve().is_file():
                    missing.append(f"{page}: {target}")
                continue
            resolved = page.parent.joinpath(target).resolve()
            if resolved.is_dir():
                resolved = resolved / "index.md"
            elif resolved.suffix == "":
                resolved = resolved.with_suffix(".md")
            try:
                relative = resolved.relative_to(DOCS.resolve()).with_suffix("").as_posix()
            except ValueError:
                continue
            if relative not in page_paths:
                missing.append(f"{page}: {target}")

    assert missing == []


def test_track49_sidebar_has_no_orphaned_pages() -> None:
    config = (ROOT / "docs-site" / "astro.config.mjs").read_text(encoding="utf-8")
    pages = {
        path.relative_to(DOCS).with_suffix("").as_posix()
        for path in _markdown_pages()
        if path.name != "docs-tooling-audit.md"
    }

    missing_from_sidebar = sorted(page for page in pages if f"'{page}'" not in config)

    assert missing_from_sidebar == []
