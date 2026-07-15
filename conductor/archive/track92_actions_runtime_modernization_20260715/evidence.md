# Track 92 Evidence

## Upstream verification

- `actions/checkout` v7.0.0 resolves to `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0`; its upstream `action.yml` declares `using: node24`.
- `actions/upload-artifact` v7.0.1 resolves to `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`; its upstream `action.yml` declares `using: node24`.
- `actions/download-artifact` v8.0.1 resolves to `3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c`; its upstream `action.yml` declares `using: node24`.

Evidence was obtained directly from the official action repositories with `git ls-remote --tags` and the tagged `action.yml` files.

## Verification

- `61` workflow references verified against the immutable allow-list: `36`
  checkout, `14` upload-artifact, and `11` download-artifact uses.
- The combined adapter, archive, publication, workflow, and SHA-policy suite
  passed: `83 passed` on Python 3.14.5 after the whole-track review added an
  assertion/embedding effective-access regression.
- Ruff check and format gates passed for all changed Python files.
- basedpyright reported `0 errors, 0 warnings, 0 notes` for the changed schema
  and policy-test surfaces.
- `git diff --check` passed.
- PR #135 passed Astro docs, agent review, auto-fix, benchmark, the complete
  Linux/macOS/Windows Python matrix, Python 3.13/3.14 experimental runtimes,
  containerized CI, manuscript review, staging, and CI-report checks.
- PR #135 was squash-merged as
  `7ce5de39f5b614377171da90cc0d6e92d319fb78` on 2026-07-16 AEST, and issue
  #134 closed automatically. The track is archive-eligible.
