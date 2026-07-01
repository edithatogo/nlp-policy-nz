# Track 54: Axiom Foundation Interoperability

**Dependencies**: Tracks 18, 22, 27
**Parallelization Node**: External Legal Source and Rules-as-Code Interoperability
**Status**: Completed

## Goal

Add selective Axiom Foundation interoperability to `nlp-policy-nz` without vendoring Axiom repositories or making the NLP package depend on the executable RuleSpec runtime.

`nlp-policy-nz` remains an independent producer project. It should emit
source-grounded NLP and provenance outputs that downstream repositories can
consume, including `rulespec-nz`, without becoming a RuleSpec runtime,
microsimulation package, or Axiom dependency bundle.

## Scope

- Add an Axiom-style source-section intermediate format for NZ legal text ingestion.
- Stamp source SHA-256 hashes and provide non-mutating staleness checks.
- Add a lightweight RuleSpec bridge for durable `nz:<path>#<concept>` references and source-verification metadata.
- Add bill/Hansard linkage scaffolding with normalized lifecycle statuses.
- Document which Axiom Foundation repositories should be used as code sources, design references, future ideas, or ignored historical references.

## Acceptance Criteria

- [x] Source-section records include authoritative URL, retrieval date, checksum, jurisdiction, document type, citation path, and optional version/title/rights metadata.
- [x] Source hash helpers compare pinned source text against current corpus text and report `current`, `stale`, or `missing` without mutating data.
- [x] RuleSpec bridge exports durable NZ concept IDs and source-verification metadata suitable for future `rulespec-nz` modules.
- [x] Bill/Hansard scaffold records bill versions, bill lifecycle actions, normalized status vocabulary, and debate-to-bill links.
- [x] Documentation records high-, medium-, low-, and ignore-for-now Axiom repo relevance tiers.
- [x] Offline tests cover source metadata, checksum behavior, staleness, `PipelineRecord` conversion, RuleSpec export, and bill/Hansard linkage.

## Out of Scope

- Vendoring Axiom repositories.
- Calling `axiom-rules-engine` from the core NLP package.
- Generating live `rulespec-nz` content.
- Owning downstream executable RuleSpec, oracle, or microsimulation outputs.
- Fetching, cloning, or executing Axiom repositories as part of default tests.
- Replacing existing Isaacus integration or Track 27 rules-as-code work.

## Axiom Differences Adopted As Conventions

- Axiom source projects emphasize durable source identity, checksums, and
  staleness checks before interpretation.
- RuleSpec projects emphasize stable legal concept IDs and source-verification
  metadata that downstream executable rules can cite.
- Axiom validation patterns include known-gap ratchets and source-coverage
  debt, not only NLP benchmark scores.
- Bill, oracle, and microsimulation projects focus on legal-effect execution;
  this track only prepares export metadata for those future consumers.

## Implemented Surfaces

- `src/nlp_policy_nz/axiom/source.py`
- `src/nlp_policy_nz/axiom/rulespec.py`
- `src/nlp_policy_nz/axiom/linkage.py`
- `docs/axiom-foundation-relevance.md`
- `tests/test_axiom_integration.py`
- `tests/fixtures/axiom/nz_source_section.txt`
