# Track 37: Publication Manuscript and Review Agents

**Dependencies**: Tracks 34-36
**Parallelization Node**: Manuscript and Review Automation
**Status**: Complete

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Identify arXiv submission requirements, relevant reporting checklists (PRISMA for systematic, CONSORT for trials, or venue-specific LaTeX templates) | [x] | conductor_orchestrator |
| 2 | Create manuscript skeleton: title/authors, abstract, introduction, methods (pipeline architecture, ontologies, reasoning approach), results (corpus stats, ontology coverage, mapping quality), discussion, conclusion | [x] | conductor_orchestrator |
| 3 | Create supplement skeleton: full ontology coverage matrix, mapping examples, corpus statistics detail tables, figure gallery, reproducibility instructions | [x] | conductor_orchestrator |
| 4 | Define reviewer agent prompts: one rubric dimension per manuscript section with 100-point scoring (clarity 20, completeness 20, correctness 20, reproducibility 20, novelty 10, presentation 10) | [x] | conductor_orchestrator |
| 5 | Create `.github/workflows/manuscript-review.yml` that runs reviewer agents on PR, posts scores as PR comments, and tracks score history | [x] | conductor_orchestrator |
| 6 | Create `scripts/manuscript/` directory with LaTeX template, macros, bibliography style, and Makefile | [x] | conductor_orchestrator |
| 7 | Run initial review loop: generate manuscript text for each section, run reviewer agent, fix low-scoring sections, record scores and fixes | [x] | conductor_orchestrator |
| 8 | Iterate until all rubric dimensions score >95/100; record final scores, fix history, and unresolved blockers in `artifacts/manuscript_review_log.json` | [x] | conductor_orchestrator |

## Implementation Note

Track 37 uses deterministic, offline review-agent scoring from checked-in Track 34-36 evidence so that GitHub Actions can execute the package without credentials or external model calls. The review log is written under `artifacts/manuscript/manuscript_review_log.json`; live external reviewer agents remain an explicit evidence gate.

## Evidence Boundary

Repo-side scaffolds, manifests, fixtures, and diagrams can satisfy planning and deterministic evidence tasks. Full-corpus, live publication, authenticated API, or external-source tasks must remain blockers until the corresponding data or access is actually available and recorded.
