# Track 76: All NZ Legislation Source Inventory

## Overview

Create the canonical source inventory required before this repository can claim it processes all New Zealand legislation for rules-as-code downstream use. The inventory must enumerate authoritative source locations, durable citation paths, retrieval status, checksums, known gaps, licensing/rights notes, and update policy for all legislation inputs expected by the NLP and extraction pipeline.

## Functional Requirements

- Define a versioned inventory schema for Acts, secondary legislation, amendments, commencement material, repeals, and known source variants.
- Implement an offline-friendly inventory builder that can run in GitHub Actions using checked-in fixtures and optional live probes.
- Emit deterministic JSON/Parquet-compatible inventory artifacts with source URL, citation path, source type, jurisdiction, effective dates when available, checksum, retrieval timestamp, and rights notes.
- Add known-gap ratchets for unavailable, malformed, PDF-only, redirected, or access-blocked sources.
- Integrate inventory output with existing source identity conventions from Tracks 27, 54, and 55.
- Document what is proved by local fixtures versus what requires live source crawling.

## Non-Functional Requirements

- Default CI behavior must be offline, deterministic, and non-networked.
- Live source probing must be opt-in and safe to skip on Windows and GitHub Actions.
- Inventory IDs must be stable across runs unless source identity changes.
- Outputs must preserve enough provenance for downstream RuleSpec, PolicyEngine, and OpenFisca promotion.

## Acceptance Criteria

- [ ] A schema and builder exist for all-legislation source inventory records.
- [ ] Fixture-backed tests cover Acts, regulations, amendments, commencement, repeals, redirects, and known gaps.
- [ ] Inventory artifacts include stable citation paths and checksum fields.
- [ ] Documentation clearly separates whole-corpus readiness from fixture-bounded evidence.
- [ ] GitHub issue and project mirror are populated for this track.

## Out of Scope

- Executable rules generation.
- Full live crawling as a required CI step.
- PolicyEngine or OpenFisca package generation.
