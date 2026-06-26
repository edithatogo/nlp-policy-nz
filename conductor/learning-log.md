# Conductor Learning Log

This log is the repository-local source of truth for repeatable learning artifacts.

## 2026-06-26 — Track gap analysis, 7 new tracks created, Track 21 improved

- **Agent**: Claude Code
- **Trigger**: `/conductor-status` audit
- **Finding**: All 37 existing tracks have matching directories. 6 active, 24 complete, 13 planned.
- **Gaps identified**: No containerization, no repo governance/contributing framework, no dependency automation/SBOM, no SAST/secrets scanning, no performance regression CI gates, no agentic automation, no data quality monitoring.
- **Actions**:
  - Created Track 38 (Containerization), 39 (Governance), 40 (Dependency Security), 41 (SAST), 42 (Perf Regression), 43 (Agentic Automation), 44 (Data Quality).
  - Improved Track 21 with Phase 7 (2026 Emerging Architectures): ModernBERT, Jamba 1.6, Llama 4/Gemma 3 MoE, RAG 2.0, DeepSeek-V3/R1, SSM encoders, test-time compute scaling.
  - Updated tracks.md with Phase IV section.
  - Committed `492a7cb` and pushed to origin/master for Jules execution.
- **Evidence**: `conductor/tracks/track{38..44}_20260626/`, `conductor/tracks/track21_bleeding_edge_architectures_20260613/plan.md` Phase 7, `conductor/tracks.md` Phase IV section.

## 2026-06-26 (late) — CI/CD maturity gap analysis, Release Engineering & Production Hardening tracks

- **Agent**: Claude Code
- **Trigger**: User asked "What did we do so far?" + CI/CD + maturity questions
- **Findings**:
  - Tracks 8 (HF Datasets), 9 (Zenodo), 24 (Multi-Git Mirroring) marked "complete" but only cover *initial* publish/upload — no CI/CD auto-publish, no incremental versioned publishing
  - Track 36 (HF Exploration Site) planned but has no CI auto-deploy workflow
  - No semantic versioning track exists (versions are entirely manual)
  - No changelog generation or release automation
  - No OSF publishing track
  - No PyPI publishing
  - No production hardening: API versioning, env separation, DB migrations, load testing, feature flags, runbook
- **Actions**:
  - Created Track 45 (Release Engineering): semantic versioning, CI/CD auto-publish to HF/Zenodo/OSF/PyPI, auto-changelog
  - Created Track 46 (Production Hardening): API v1/v2, dev/staging/prod, DB migrations, load testing, feature flags, health endpoints, runbook
  - Updated tracks.md with Phase V section and execution-order diamond dependency diagram
- **Evidence**: `conductor/tracks/track45_release_engineering_20260626/`, `conductor/tracks/track46_production_hardening_20260626/`, `conductor/tracks.md` Phase V.

## 2026-06-26 (night) — Full maturity gap closure: Cross-Platform CI, Client SDK, Docs Site, Compliance

- **Agent**: Claude Code
- **Trigger**: User asked to continue creating/improving tracks until all maturity requirements covered
- **Audit findings from reading actual server code (`src/nlp_policy_nz/api/server.py`)**:
  - FastAPI server exists with `/health`, `/embed`, `/search`, `/process` but NO versioned routes
  - Version string hardcoded `"0.1.0"` — not from VERSION.json
  - Health endpoint only checks model loaded, not DB or pipeline status
  - No CORS middleware, no rate limiting, no graceful shutdown
  - Sync pipeline calls inside async handlers (potential event loop blocking)
  - CI only runs on ubuntu-latest; developer platform is Windows
  - No client SDK, no shell completion, no developer quickstart
  - No docs site, no API reference, no user guides, no tutorial notebooks
  - No WCAG accessibility audit for Gradio Space
  - No Privacy Act compliance documented
- **Gaps filled with 4 new tracks (47-50)**:
  - Track 47 (Cross-Platform CI): multi-OS CI matrix, binary builds, platform-specific fixes
  - Track 48 (Client SDK): Python client library, CLI completion, Docker Compose stack, quickstart
  - Track 49 (Documentation Site): MkDocs/ReadTheDocs, auto-generated API ref, user guides, tutorials, runbook
  - Track 50 (Compliance & Accessibility): WCAG 2.1 AA, Privacy Act, a11y CI scan
- **Enriched existing tracks**:
  - Track 38 (Containerization): added multi-arch build, HEALTHCHECK, non-root user, hadolint
  - Track 39 (Governance): added CODE_OF_CONDUCT, SECURITY.md, CLA/DCO check
  - Track 46 (Production Hardening): upgraded all tasks with server audit specifics (CORS, async safety, uvicorn workers, slowapi rate limiting, broader health check)
- Updated tracks.md with Phase VI section and full dependency diagram for all 50 tracks
- Updated Makefile with `conductor-status` target (replaces `track-status`)
- **Final state**: 50 tracks across 6 phases — all maturity-critical features now covered in roadmap
- **Evidence**: `conductor/tracks/track{47..50}_*`, enriched `track{38,39,46}`, `conductor/tracks.md` Phase VI, `Makefile` conductor-status target.

## 2026-06-23 — Track 18 rollout (self-learning loop implementation)
- `entry_id`: `track-18-root-legal-nz`
- `observed_on`: 2026-06-23
- `repo`: `legal-nz`
- `scope`: `track`
- `trigger`: `Track 18 implementation requires shared loop artifacts and repository-local learning surfaces`
- `severity`: `low`
- `status`: `resolved`
- `lessons_learned`:
  - Self-learning improvements need a machine-readable schema before CI automation can reason about logs.
  - Track templates without `lessons_learned` / `next_check_to_add` fields are difficult to promote safely.
  - Multiple conductor repos in this workspace need mirrored learning surfaces to avoid hidden gaps.
- `next_check_to_add`:
  - Add CI validation that checks the schema for every `learning-log.md` entry.
  - Add a lightweight step to emit learning candidates from failing workflows into `improvement-backlog.md`.
- `evidence`:
  - `conductor/templates/self-improvement-loop.md`
  - `conductor/templates/learning-entry.schema.json`
  - `conductor/templates/track-improvement-template.md`
  - `conductor/learning-log.md`
  - `conductor/improvement-backlog.md`
