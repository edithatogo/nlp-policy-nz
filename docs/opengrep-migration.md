# OpenGrep SAST migration (20 November 2026)

Replaces the actively executed Semgrep Python CLI with the SHA-256-verified
standalone OpenGrep v1.33.1 Linux x86_64 executable. A dedicated
`.github/workflows/opengrep.yml` now scans PRs and master pushes with
read-only permissions and synthetic positive and negative controls.
The previous `p/python` registry pack, WARNING threshold, complete source
target and blocking outcome are retained, with stricter parser-error handling.

`make security-sast` runs Bandit and OpenGrep, and the Python development
extra no longer requests Semgrep. Existing Bandit, secrets, dependency and
SBOM workflows remain unchanged.

**Follow-up hold:** `pixi.toml` and `pixi.lock` retain an unused optional
`security` feature containing Semgrep. The normal `py311`/`py312`
environments do not include it. Removing it requires an atomic supported
Pixi lock regeneration, not manual lock edits or weakening `--frozen`.
This migration is not evidence that the old dependency disappeared from
the entire optional dependency graph.

**Rule-source hold:** the legacy `p/python` registry ruleset is dynamically
resolved. Before calling the new scanner rule-equivalent, capture full
rule-ID, parser-skip and finding-parity receipts against a pinned Semgrep
reference and select licence-compatible immutable rule snapshots. Never
silently suppress new findings. The open PR and workflow definition alone
are not proof of successful execution; inspect the exact-head GitHub check
before adding the new required status context to branch protection.

For local use, install an independently verified OpenGrep build appropriate
to your platform, then run `make security-sast`.
