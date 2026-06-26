# Track 49: Documentation Site & Knowledge Base

**Dependencies**: Tracks 7, 23, 39, 45, 46, 47, 48
**Parallelization Node**: Developer Experience
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Scaffold MkDocs project with Material theme in `docs/`; add auto-deploy GitHub Actions workflow | [ ] | conductor_orchestrator |
| 2 | Configure mkdocstrings to extract Python API reference from `src/nlp_policy_nz/` docstrings | [ ] | conductor_orchestrator |
| 3 | Publish OpenAPI spec as API reference page (link or auto-generate from `/openapi.json`) | [ ] | conductor_orchestrator |
| 4 | Write user guides: installation, quickstart, ingestion, ontology, search, publishing, client SDK | [ ] | conductor_orchestrator |
| 5 | Write architecture docs: system overview (C4), data flow, ontology mapping, security | [ ] | conductor_orchestrator |
| 6 | Write operations runbook: deployment, monitoring, backup/restore, failure recovery | [ ] | conductor_orchestrator |
| 7 | Create 3+ tutorial Jupyter notebooks in `docs/notebooks/`; configure mkdocs-jupyter plugin | [ ] | conductor_orchestrator |
| 8 | Verify versioned docs: build per git tag; add version selector widget | [ ] | conductor_orchestrator |
| 9 | Write smoke test that checks all internal links resolve and no pages are orphaned | [ ] | conductor_orchestrator |

## Evidence Boundary

MkDocs config, all guide/architecture/runbook markdown, tutorial notebooks, and auto-deploy workflow satisfy repo-side evidence. Live hosting on ReadTheDocs/GitHub Pages requires org-level configuration.
