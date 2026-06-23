# Quality and Maintenance Tooling Baseline — nlp-policy-nz

| Tool               | Required | Status    | Notes                                               |
|--------------------|----------|-----------|------------------------------------------------------|
| Vale               | required | ✅ Present | `.vale.ini` — `MinAlertLevel = warning`, Microsoft package |
| Markdown style     | required | ✅ Added  | `.markdownlint.json` created from root template      |
| Renovate           | required | ✅ Added  | `renovate.json` created (based on cli-legislation-nz template) |
| Codecov            | conditional | ❌ Not ready | No `codecov.yml` — coverage via `.coveragerc` + `pyproject.toml` but no upload configured |
| Scalene            | required | ⚠️ Partial | Listed as dev dependency (`scalene>=1.5.0`) but no `[tool.scalene]` config section |
