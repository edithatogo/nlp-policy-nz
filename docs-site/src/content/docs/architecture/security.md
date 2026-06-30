---
title: Security architecture
description: Threat model and security boundaries.
---

# Security architecture

Primary risks:

- Untrusted text or XML input from public legal sources.
- Accidental publication of private corpus material or credentials.
- Unsafe archive, upload, or deployment tokens in CI.
- Dependency and supply-chain drift.

Controls:

- Prefer `defusedxml` and structured parsers for XML.
- Keep secrets in CI secret stores, not files.
- Publish provenance and checksums with datasets.
- Run SAST, dependency, benchmark, and data-quality tracks before production
  releases.
