# Track 49 Evidence: Documentation Site and Knowledge Base

## Implemented artifacts

- `docs-site/astro.config.mjs`: expanded Starlight sidebar covering start pages, guides, reference, architecture, operations, tutorials, and audit material.
- `.github/workflows/docs.yml`: docs build, generated reference step, tag trigger, and GitHub Pages deployment on `master`.
- `scripts/generate_docs_reference.py`: generated OpenAPI JSON, OpenAPI markdown, Python API index, and CLI reference pages.
- `docs-site/src/content/docs/index.md`: site home page linking all major user sections.
- `docs-site/src/content/docs/installation.md`: installation guide.
- `docs-site/src/content/docs/quickstart.md`: five-minute quickstart.
- `docs-site/src/content/docs/guides/ingestion.md`: ingestion guide.
- `docs-site/src/content/docs/guides/ontology.md`: ontology guide.
- `docs-site/src/content/docs/guides/search.md`: search guide.
- `docs-site/src/content/docs/guides/publishing.md`: publishing guide.
- `docs-site/src/content/docs/guides/client-sdk.md`: client SDK guide.
- `docs-site/src/content/docs/api/openapi.md`: generated OpenAPI reference page.
- `docs-site/src/content/docs/api/openapi.json`: generated OpenAPI document.
- `docs-site/src/content/docs/api/python.md`: generated Python API index.
- `docs-site/src/content/docs/api/cli.md`: generated CLI reference.
- `docs-site/src/content/docs/architecture/system-overview.md`: C4-style subsystem overview with Mermaid diagram.
- `docs-site/src/content/docs/architecture/data-flow.md`: ingestion-to-publication data flow.
- `docs-site/src/content/docs/architecture/ontology-kg.md`: ontology mapping and knowledge graph design.
- `docs-site/src/content/docs/architecture/security.md`: security architecture and threat model.
- `docs-site/src/content/docs/architecture/adr.md`: decision record index.
- `docs-site/src/content/docs/operations/runbook.md`: deployment, monitoring, backup, restore, and failure recovery runbook.
- `docs-site/src/content/docs/versioning.md`: latest/tag versioning guidance.
- `docs-site/src/content/docs/tutorials/hansard-stance-citations.md`: tutorial page linked to notebook.
- `docs-site/src/content/docs/tutorials/semantic-legislation-search.md`: tutorial page linked to notebook.
- `docs-site/src/content/docs/tutorials/policy-argument-trace.md`: tutorial page linked to notebook.
- `docs/notebooks/hansard_stance_citations.ipynb`: tutorial notebook artifact.
- `docs/notebooks/semantic_legislation_search.ipynb`: tutorial notebook artifact.
- `docs/notebooks/policy_argument_trace.ipynb`: tutorial notebook artifact.
- `tests/test_track49_docs_site.py`: docs structure, generated reference, notebook, workflow, link, and orphan tests.
- `tests/test_track49_conductor.py`: conductor registry, metadata, plan/spec, and evidence tests.

## Acceptance evidence

- Docs deploy automatically on master merge through `.github/workflows/docs.yml`.
- API reference pages are generated from local FastAPI and CLI entry points when dependencies are available, with explicit fallback output for minimal docs builds.
- Installation, quickstart, ingestion, ontology, search, publishing, and client SDK guides are written and linked from the site.
- Architecture pages include subsystem and data-flow Mermaid diagrams plus ontology, security, and ADR pages.
- Three tutorial notebook artifacts exist and are linked from rendered tutorial pages.
- Operations runbook covers deploy, monitoring, backup, restore, and failure recovery.
- Versioning page and docs workflow tag trigger document latest/tag behavior.

## Validation

- `.\.venv\Scripts\python.exe scripts\generate_docs_reference.py` passed and generated OpenAPI, Python API, and CLI reference pages.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track49_docs_site.py tests\test_track49_conductor.py` passed: 10 tests.
- `.\.venv\Scripts\python.exe -m ruff check scripts\generate_docs_reference.py tests\test_track49_docs_site.py tests\test_track49_conductor.py` passed.
- `npm install --prefix docs-site --no-audit --no-fund` passed and produced `docs-site/package-lock.json`.
- `npm run docs:check` passed with 0 Astro diagnostics.
- `npm run docs:build` passed and built 23 pages with Pagefind search index.
- After strengthening generated Python docstring extraction, `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track49_docs_site.py tests\test_track49_conductor.py tests\test_quality_infrastructure.py` passed: 15 tests.
- After strengthening generated Python docstring extraction, `npm run docs:check` and `npm run docs:build` passed again; the build produced 23 pages and a Pagefind search index.

## Review and archive validation

- Review fix applied: `.github/workflows/docs.yml` now installs Python package dependencies and runs reference generation with `PYTHONPATH=src`, preventing CI from silently falling back to minimal reference output.
- Review fix applied: `scripts/generate_docs_reference.py` now renders static tutorial pages from `docs/notebooks/*.ipynb`, so tutorial notebooks are represented as docs-site pages rather than link-only artifacts.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track49_docs_site.py tests\test_track49_conductor.py tests\test_quality_infrastructure.py` passed after review fixes: 15 tests.
- `.\.venv\Scripts\python.exe -m ruff check scripts\generate_docs_reference.py tests\test_track49_docs_site.py tests\test_track49_conductor.py` passed after review fixes.
- `npm run docs:check` and `npm run docs:build` passed after review fixes; the build produced 23 pages and a Pagefind search index.
- `.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track49_docs_site.py tests\test_track49_conductor.py tests\test_quality_infrastructure.py` passed after archive: 15 tests.
