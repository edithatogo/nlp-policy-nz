# Axiom Foundation Relevance

This note records which Axiom Foundation repositories are useful to
`nlp-policy-nz` and how they should be used. The decision is selective reuse:
borrow source identity, provenance, validation, and executable-law integration
patterns without copying Axiom repositories or making the NLP package depend
on the RuleSpec runtime.

`nlp-policy-nz` stays its own project. Its role is to produce source-grounded
NLP, corpus, benchmark, and publication outputs that other projects can
consume. Axiom compatibility means stable export shapes and shared provenance
conventions, not shared ownership, runtime coupling, or executable-law logic in
this package.

## Repository Tiers

| Tier | Repositories | Use in `nlp-policy-nz` |
| --- | --- | --- |
| High value | `rulespec-nz`, `axiom-corpus`, `axiom-scrapers`, `axiom-encode`, `axiom-rules-engine` | NZ source identity, source-section metadata, staleness checks, RuleSpec references, and future executable-law evaluation boundaries. |
| Medium value | `axiom-bills`, `axiom-compose`, `rulespec-us`, `rulespec-uk`, `axiom-oracles`, `axiom-microsim` | Bill/Hansard lifecycle ideas, mature validation conventions, deterministic composition ideas, and later oracle comparison patterns. |
| Low value / UI only | `axiom-foundation.org`, `design-system`, `rulespec-graph-viewer`, `axiom-architecture`, demo and playground repositories | Useful only when this repository grows a public graph, source, or RuleSpec explorer. |
| Ignore for now | archived or absorbed repositories such as `rulespec-us-*`, `rulespec-compile`, `rulespec-validators`, `statute-graph`, `akomize`, `atlas-viewer`, `rulespec-syntax`, `axiom-claude` | Historical reference only unless a specific missing feature requires archaeology. |

## Source Identity Convention

`nlp-policy-nz` should use Axiom-style identity for source-grounded records:

- `citation_path`: stable corpus path such as `nz/statutes/example-act/2026/5`.
- RuleSpec durable ID: `nz:<path>#<concept>`, with the leading `nz/` removed
  from the path, for example `nz:statutes/example-act/2026/5#obligation`.
- `source_sha256`: SHA-256 of normalized source text, used to detect stale
  source-grounded records without mutating data.
- Source metadata: authoritative address, retrieval timestamp, jurisdiction,
  document type, title/version/effective-date fields when available, and rights
  notes when known.
- RuleSpec export candidates must keep `module.source_verification` compatible
  with `rulespec-nz`: use `corpus_citation_path` or `corpus_citation_paths` as
  source locators, and keep raw URLs, retrieval timestamps, and checksum pins in
  adjacent provenance metadata rather than legacy `source_url` fields.

The local implementation lives in `nlp_policy_nz.axiom`:

- `source.py`: source-section metadata, checksum stamping, staleness reports,
  and conversion into `PipelineRecord`.
- `rulespec.py`: lightweight RuleSpec durable IDs and source-verification
  metadata for future `rulespec-nz` exports.
- `linkage.py`: normalized bill lifecycle status and Hansard-to-bill link
  records.

## Integration Decision

Don't copy Axiom repositories into `nlp-policy-nz`. Don't make
`axiom-rules-engine` a core dependency yet. The current package remains the
NLP, corpus, benchmark, and publication layer; executable RuleSpec content
belongs in `rulespec-nz`.

In practical terms, this package is a producer:

- it ingests or receives NZ legal text;
- it normalizes source identity and provenance;
- it emits `PipelineRecord`, JSON-LD bridge records, source checksum reports,
  and optional non-executable package skeletons;
- it leaves executable RuleSpec modules, policy formulas, oracle comparison,
  and runtime evaluation to downstream projects.

Axiom projects tend to make different choices:

- source repositories preserve legal text as durable, checksum-pinned source
  sections before higher-level interpretation;
- RuleSpec repositories treat legal provisions as durable concept IDs and
  executable or near-executable rule modules;
- validation is ratcheted through known source gaps and source-verification
  metadata, not only through model metrics;
- bill, oracle, and simulation projects are organized around downstream
  legal-effect evaluation rather than NLP preprocessing.

Use Axiom conventions where they improve interoperability:

- source-section metadata and source hash pins from `axiom-scrapers` /
  `axiom-encode`;
- durable `nz:` concept IDs compatible with `rulespec-nz`;
- bill lifecycle normalization ideas from `axiom-bills`;
- known-gap ratchet ideas from `rulespec-us` and `rulespec-uk`.

## Adoption Status

Already adopted in this repository:

- source-section text plus metadata records;
- normalized source text hashing and staleness reports;
- durable `nz:<path>#<concept>` references for downstream RuleSpec consumers;
- RuleSpec-compatible source-verification metadata that avoids legacy
  `source_url` fields under `module.source_verification`;
- bill lifecycle and Hansard-to-bill linkage scaffolding;
- offline `rac-export` JSON-LD bridge output;
- non-executable OpenFisca/PolicyEngine-style package skeletons;
- no Axiom runtime dependency or repository copying.

Useful Axiom approaches not yet fully adopted:

- broad extractor manifests for all output families, such as definitions,
  obligations, prohibitions, permissions, powers, conditions, exceptions,
  eligibility rules, thresholds, dates, entities, amendments, commencement,
  repeal, cross-references, penalties, delegations, and review rights;
- YAML/JSON schema contracts for each extracted data family;
- known-gap ratchets for corpus coverage, parser gaps, and extraction debt;
- source-to-output trace manifests that map every extracted record back to a
  checksum-pinned source span;
- optional PDF and OCR ingestion, using libraries such as `pypdf` only when the
  input source requires it;
- optional durable local extraction catalogs, using SQLite-style storage if the
  corpus grows beyond simple file artifacts;
- executable-rule or oracle comparison, which should remain downstream until
  reviewed NZ RuleSpec or PolicyEngine/OpenFisca semantics exist.

Candidate libraries from Axiom projects:

- `pydantic`: useful for stricter public export schemas, but this repository
  currently uses data classes plus existing serialization helpers and shouldn't
  switch wholesale without a schema migration.
- `PyYAML` or `ruamel.yaml`: useful if extractor manifests or RuleSpec
  handoff files become YAML-first. JSON-LD remains the current bridge format.
- `pypdf`: useful for official PDF files that can't be sourced as text, HTML, or
  XML. It should be optional rather than a core dependency.
- Python standard library `sqlite3`: useful for local source catalogs, extraction
  run indexes, and staleness audit state. This is a good future candidate.
- Rust `serde`, `serde_json`, `serde_yaml`, `chrono`, and `rust_decimal`:
  useful patterns for a future executable rules engine, but not needed in this
  NLP package now.
- `policyengine`, `policyengine-taxsim`, and Axiom oracle adapters: downstream
  comparison tools, not core dependencies for this repository.

## Future Tracks

- RuleSpec-assisted legal effect evaluation: use encoded NZ provisions from
  `rulespec-nz` as gold or silver labels for modality and legal-effect
  tasks.
- Corpus coverage dashboard: adapt known-gap ratchets for NZ source coverage,
  parser debt, source staleness, and validation gaps.
- Deterministic policy composition: revisit `axiom-compose` only if this
  repository begins assembling executable policy programs from extracted
  provisions.
- Oracle comparison: revisit `axiom-oracles` and `axiom-microsim` after NZ
  tax-benefit or eligibility outputs become a target.
- UI and graph visualization: defer `rulespec-graph-viewer`,
  `axiom-foundation.org`, and `design-system` until there is a user-facing
  RuleSpec or knowledge-graph explorer.
