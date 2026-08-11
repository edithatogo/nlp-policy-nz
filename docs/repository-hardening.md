# Repository hardening

The machine-readable control inventory is
`data/quality/repository_hardening_manifest.json`. It distinguishes controls
implemented in the repository from hosted settings that require repository
administrator action.

The repository-side gate is `.github/workflows/repository-hardening.yml`. It
runs a bounded metamorphic test for normalization idempotence and validates the
hardening manifest. The mutation lane remains available through the existing
explicit `pixi run mutation` dispatch path because running it on every pull
request would exceed the fast-lane budget.

Rulesets, Renovate app access, and Codecov OIDC activation cannot be created by
committing files. Their status must be verified through GitHub and provider
receipts before issues #232 and #233 are closed.
