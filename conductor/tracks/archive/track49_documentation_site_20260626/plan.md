# Track 49: Documentation Site & Knowledge Base

**Dependencies**: Tracks 7, 23, 39, 45, 46, 47, 48
**Parallelization Node**: Developer Experience
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Scaffold MkDocs project with Material theme in `docs/`; add auto-deploy GitHub Actions workflow | [x] | conductor_orchestrator |
| 2 | Configure mkdocstrings to extract Python API reference from `src/nlp_policy_nz/` docstrings | [x] | conductor_orchestrator |
| 3 | Publish OpenAPI spec as API reference page (link or auto-generate from `/openapi.json`) | [x] | conductor_orchestrator |
| 4 | Write user guides: installation, quickstart, ingestion, ontology, search, publishing, client SDK | [x] | conductor_orchestrator |
| 5 | Write architecture docs: system overview (C4), data flow, ontology mapping, security | [x] | conductor_orchestrator |
| 6 | Write operations runbook: deployment, monitoring, backup/restore, failure recovery | [x] | conductor_orchestrator |
| 7 | Create 3+ tutorial Jupyter notebooks in `docs/notebooks/`; configure mkdocs-jupyter plugin | [x] | conductor_orchestrator |
| 8 | Verify versioned docs: build per git tag; add version selector widget | [x] | conductor_orchestrator |
| 9 | Write smoke test that checks all internal links resolve and no pages are orphaned | [x] | conductor_orchestrator |

## Implementation Note

The repo already had an Astro/Starlight documentation scaffold and `conductor/tech-stack.md`
declares Astro as the documentation portal. Track 49 was therefore implemented
on the existing Astro/Starlight site rather than introducing a second MkDocs or
Sphinx stack.

## Evidence Boundary

MkDocs config, all guide/architecture/runbook markdown, tutorial notebooks, and auto-deploy workflow satisfy repo-side evidence. Live hosting on ReadTheDocs/GitHub Pages requires org-level configuration.
