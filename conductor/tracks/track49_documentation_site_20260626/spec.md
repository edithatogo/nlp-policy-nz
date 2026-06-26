# Track 49: Documentation Site & Knowledge Base

**Dependencies**: Tracks 7, 23, 39, 45, 46, 47, 48
**Parallelization Node**: Developer Experience
**Status**: Planned

## Goal

Build a comprehensive, searchable, versioned documentation site covering everything a user, contributor, or operator needs — API reference, user guides, architecture docs, tutorials, and runbook.

## Scope

### 1. Documentation Framework & Hosting
- MkDocs with Material theme or Sphinx with ReadTheDocs
- Auto-deploy on master merge via GitHub Actions
- Versioned docs matching git tags
- Search, dark mode, mobile-responsive

### 2. Auto-Generated API Reference
- OpenAPI/Swagger spec auto-published from FastAPI (`/openapi.json`)
- Python API reference extracted from docstrings (sphinx-autodoc or mkdocstrings)
- CLI reference with all subcommands and flags

### 3. User Guides
- Installation guide (pip, pixi, Docker, binary)
- Quickstart (5-minute tutorial)
- Ingestion guide: importing legislation and Hansard corpora
- Ontology guide: deontic, temporal, entity, argument, stance
- Search guide: semantic search, vector queries, filtering
- Publishing guide: HF, Zenodo, OSF workflows
- Client SDK guide: using the Python client

### 4. Architecture & Design Docs
- System architecture overview (C4 model diagrams)
- Data flow: ingestion → pipeline → storage → search → publish
- Ontology mapping and knowledge graph design
- Decision records (ADRs) for key technical choices
- Security architecture and threat model

### 5. Operations & Runbook
- Deployment guide for staging/production
- Monitoring and alerting setup
- Backup and restore procedures
- Common failure modes and recovery

### 6. Tutorial Notebooks
- Jupyter notebooks in `docs/notebooks/` rendered as static pages
- Example: "Analyze a Hansard debate for stance and citations"
- Example: "Search legislation by semantic similarity"
- Example: "Trace argument structure across a policy document"

## Acceptance Criteria

- [ ] Docs site deploys automatically on master merge
- [ ] API reference auto-generated from OpenAPI spec + Python docstrings
- [ ] All user guides from Scope 3 are written and linked from site home page
- [ ] Architecture diagrams (C4 level 2) explain all major subsystems
- [ ] 3+ tutorial notebooks render correctly in the docs site
- [ ] Runbook covers deploy, backup, restore, and failure recovery
- [ ] Docs versioned per git tag; "latest" points to master
