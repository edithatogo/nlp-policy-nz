# Track 9: Establish Citable Zenodo Archives & Release Workflows

**Dependencies**: Track 8 (Hugging Face Datasets & Visualization Spaces)
**Parallelization Node**: Zenodo API Deposit Registry
**Status**: 🔄 In Progress

---

## Goal

Provide a polished, documented release workflow that allows researchers to create versioned, citable Zenodo archives of processed NZ legislative and Hansard corpora. The system shall support both the **Zenodo Sandbox** (for testing) and **Zenodo Production** (for real DOIs), and integrate with the existing CLI and GitHub Actions CI.

## Scope

### What This Track Covers

1. **Zenodo Production API Support**: Extend the existing Sandbox-only client (`integrations/zenodo.py`) to also support the production Zenodo API endpoint and token environment variable.
2. **CLI Subcommand Tests**: Add comprehensive tests for the `archive-to-zenodo` and `release` CLI subcommands.
3. **Automated GitHub Actions Release Workflow**: A CI/CD pipeline that, on tag push (e.g. `v1.0.0`), creates a release archive from pipeline outputs and publishes it to Zenodo.
4. **Release Script**: A convenience shell script for local one-shot releases.
5. **Documentation Updates**: Update `product.md`, `requirements.md`, and `README.md` to document the Zenodo archive and release workflow.
6. **Track Formalisation**: Create the track directory, spec, and plan with phased checklist.

### What This Track Does NOT Cover

- Loading data from Zenodo (read-only access is out of scope)
- Fine-grained deposit versioning or DOI versioning (single-shot deposits)
- Authentication / token management UI (token must be set via env var)
- HF ↔ Zenodo automatic cross-linking (manual DOI entry in dataset cards is acceptable)

## Acceptance Criteria

- [ ] `ZENODO_PRODUCTION_URL` and `ZENODO_PRODUCTION_TOKEN` constants exist alongside existing Sandbox variants
- [ ] `ZenodoArchiver` and `archive_to_zenodo` accept an optional `environment="sandbox" | "production"` parameter
- [ ] CLI `archive-to-zenodo` subcommand has passing tests covering arg parsing and handler dispatch
- [ ] CLI `release` subcommand has passing tests covering arg parsing and handler dispatch
- [ ] GitHub Actions release workflow exists at `.github/workflows/release.yml`
- [ ] Release script exists at `scripts/release.sh` (or equivalent) with dry-run mode
- [ ] `product.md`, `requirements.md`, and `README.md` reflect the new Zenodo/release capabilities
- [ ] All new code passes `ruff check`, coverage > 90%, and mutation testing
