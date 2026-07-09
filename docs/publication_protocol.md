# Standards-Based Publication Protocol

This protocol defines how `nlp-policy-nz` publications should describe the
repository pipeline, standards coverage, ontology strategy, rules-as-code bridge,
analysis artifacts, reproducibility surface, and limitations. It is deliberately
evidence-bound: every publication claim must be linked to checked-in repository
evidence, external evidence, planned work, or an explicit blocker.

## Publication boundary

`nlp-policy-nz` is the NLP, corpus, benchmark, and publication-output producer
for New Zealand legal and parliamentary text. It can publish repository-side
methods, schemas, fixtures, deterministic artifacts, and quality gates. It must
not describe fixture-bounded outputs as full-corpus results, and publications
must not claim executable rules-as-code behavior for bridge records that are
intended for downstream projects.

The machine-readable claim map is
`data/publication/track34_protocol_evidence_map.json`.

## Repository overview

The repository is organized around a staged pipeline:

- ingestion, normalization, syntactic processing, semantic processing, storage,
  search, downstream exports, and archival release work;
- standards-oriented enrichment for Akoma Ntoso, PROV-O, FOAF/SIOC, Wikidata,
  ontology mapping, Axiom-compatible source identity, and downstream bridge
  records;
- deterministic analysis artifacts for ontology coverage, corpus statistics,
  graph/vector alignment, benchmark baselines, and documentation publishing.

Repository-side methods are evidenced by completed Conductor track artifacts
under `conductor/tracks/archive/`, implementation modules under
`src/nlp_policy_nz/`, tests under `tests/`, checked-in data under `data/`, and
documentation under `docs/`.

## Reproducibility instructions

Use a clean checkout and keep external credentials optional. The default
publication protocol is offline-first and should be reproducible without live
corpus downloads, paid model endpoints, authenticated APIs, or local vector
stores.

1. Install the project environment with `pixi install`.
2. Run focused repository checks with `pixi run test` and `pixi run lint`, or
   the equivalent `.venv\Scripts\python.exe -m pytest` and
   `.venv\Scripts\python.exe -m ruff check` commands used by CI.
3. Regenerate deterministic Track 32 statistics with
   `nlp-policy-nz corpus-stats --output-dir data/statistics`.
4. Regenerate deterministic Track 33 graph/vector artifacts with
   `nlp-policy-nz graph-vector-analysis --output-dir data/analysis`.
5. Check documentation with the `Docs` GitHub Actions workflow or the local docs
   commands recorded in the documentation site track.
6. Treat missing full corpora, external credentials, full LanceDB indexes, and
   live publication services as blockers unless their artifacts are supplied and
   recorded.

## Evidence classes

| Evidence class | Meaning | Publication wording |
| --- | --- | --- |
| `repo_evidence` | Checked-in implementation, tests, data, docs, or Conductor evidence substantiate the claim. | "The repository implements..." or "The checked-in artifact records..." |
| `external_evidence` | Evidence exists outside the repository and must be cited directly. | "External evidence indicates..." |
| `planned_work` | The capability is tracked but not complete. | "Planned work will..." |
| `blocker` | The claim is intentionally limited by missing corpus, credentials, external service access, or live data. | "Current evidence is bounded by..." |

## Standards compliance matrix

| Standard or convention | Status | Evidence |
| --- | --- | --- |
| Akoma Ntoso v3 | Repository evidence | `conductor/tracks/archive/track14_akoma_ntoso_v3_20260613/evidence.md` |
| PROV-O provenance | Repository evidence | `conductor/tracks/archive/track15_prov_o_provenance_20260613/evidence.md` |
| FOAF and SIOC discourse | Repository evidence | `conductor/tracks/archive/track16_faaf_sioc_discourse_20260613/evidence.md` |
| Wikidata integration | Repository evidence | `conductor/tracks/archive/track17_wikidata_integration_20260613/evidence.md` |
| Ontology coverage and mapping | Repository evidence | `data/ontologies/coverage_manifest.json`, `docs/ontology_mapping.md`, `docs/nz_ontologies.md` |
| Axiom source identity and RuleSpec bridge conventions | Repository evidence | `docs/axiom-foundation-relevance.md`, `src/nlp_policy_nz/axiom/`, `src/nlp_policy_nz/cli/main.py` (`rac-export`) |
| FAIR-style publication metadata | Repository evidence plus planned work | `docs/multi_archive_strategy.md`, `conductor/tracks/archive/track9_zenodo_20260609/evidence.md`, Tracks 35-37 |
| Full-corpus statistics | Blocker | `data/statistics/corpus_statistics_blockers.json` |
| Full graph/vector analysis | Blocker | `data/analysis/graph_vector_blockers.json` |

## Ontology and reasoning strategy

Publications should describe ontology work as a repository-evidenced scaffold and
analysis layer:

- Track 25 records coverage and standards gaps.
- Track 29 records ontology mapping graph artifacts.
- Track 30 records inferred mapping candidates.
- Track 31 records New Zealand-specific ontology candidates and controlled
  vocabularies.
- Track 54 records Axiom-compatible source identity, source checksums, and
  lightweight RuleSpec bridge metadata.

Do not claim that ontology artifacts are complete for every New Zealand legal or
parliamentary source. Use the blocker registers in
`data/ontologies/data_blocker_register.json` and
`data/ontologies/ontology_implementation_backlog.json` to identify planned or
blocked coverage.

## Rules-as-code bridge

Rules-as-code outputs in this repository are source-grounded bridge records, not
an executable RuleSpec runtime. Durable IDs, source verification metadata,
source hashes, bill/Hansard linkage shapes, and JSON-LD bridge exports are
appropriate publication claims. Executable legal-effect evaluation belongs in
downstream projects such as `rulespec-nz` unless this repository later adds a
reviewed executable use case.

## Interface surfaces and downstream use

Publications and the manuscript package should describe how adjacent datasets
and downstream systems consume this repository:

- GitHub Actions is the default automation surface for validation, packaging,
  and release checks.
- The CLI is the primary human operator surface.
- The HTTP API and Python SDK are programmatic surfaces for callers that need
  reusable functions instead of shell steps.
- MCP is the agent-facing read-only surface and should remain a thin adapter
  over core helpers.
- Exported datasets and checked-in artifacts are the preferred interchange
  format for downstream policy-engine, OpenFisca, or other rules-as-code
  workflows.

## Comparative tooling and runtime choices

When the paper discusses implementation choices, it should include a compact
comparison matrix and keep the justification evidence-bound:

- LanceDB is the default local vector store because it keeps CI and local
  reproduction simple.
- Qdrant remains an optional service backend for deployments that explicitly
  need remote vector-service semantics.
- Polars and Arrow-backed transforms should be described as the default
  tabular-analysis path when they are used.
- Generic ingestion libraries such as Unstructured should be framed as optional
  future adapters, not as required paper dependencies, unless they are actually
  committed and reviewed in-tree.
- Mojo, vLLM, or other experimental acceleration paths should be presented as
  staged options, not as prerequisites for the repository's baseline results.

## Corpus statistics methodology

Track 32 produces deterministic descriptive statistics from supplied
`PipelineRecord` Parquet inputs or local fixtures. The checked-in report records
per-corpus coverage, temporal coverage, ontology coverage, and blockers. In
publication wording, describe the current output as fixture-bounded unless a
publication run supplies and records canonical whole-corpus Parquet exports.

## Graph and vector methodology

Track 33 produces deterministic graph, vector, network, and alignment analysis
from checked-in ontology artifacts and deterministic vector fixtures. It reports
centrality, communities, vector nearest neighbors, PCA-style projections,
cluster assignments, graph/vector alignment, and blockers. In publication
wording, describe the current output as fixture-bounded unless a publication run
supplies canonical full graph exports and vector indexes.

## Artifact inventory

| Artifact family | Paths |
| --- | --- |
| Publication protocol | `docs/publication_protocol.md`, `data/publication/track34_protocol_evidence_map.json` |
| Ontology coverage | `data/ontologies/coverage_manifest.json`, `data/ontologies/data_blocker_register.json`, `data/ontologies/ontology_implementation_backlog.json` |
| Ontology outputs | `data/ontologies/ontology_mappings.json`, `data/ontologies/inferred_mapping_candidates.json`, `data/ontologies/nz_ontology_candidates.json` |
| Corpus statistics | `data/statistics/corpus_statistics_manifest.json`, `data/statistics/corpus_statistics_blockers.json`, `docs/corpus_statistics.md` |
| Graph/vector analysis | `data/analysis/graph_vector_manifest.json`, `data/analysis/graph_vector_blockers.json`, `docs/graph_vector_network_analysis.md` |
| Axiom bridge | `docs/axiom-foundation-relevance.md`, `src/nlp_policy_nz/axiom/`, `src/nlp_policy_nz/cli/main.py` (`rac-export`) |
| Quality gates | `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.github/workflows/benchmark-update.yml` |

## Limitations and blocker policy

The protocol requires explicit limitations for:

- missing full-corpus Parquet exports;
- missing full citation, co-vote, co-speech, Wikidata, graph, or vector exports;
- live publication services and authenticated APIs;
- external corpus access or source material that cannot be checked into the
  repository;
- planned Tracks 35-37 outputs, including final figures, an exploration site,
  and manuscript automation.

When a publication claim depends on one of these inputs, cite the relevant
blocker file and use planned or blocked wording. Do not convert a blocker into a
result without adding the supporting artifact and updating the evidence map.

## Overclaim review checklist

Before publication, check that:

- every claim appears in `data/publication/track34_protocol_evidence_map.json`;
- every `repo_evidence` path exists in the checkout;
- fixture-bounded Track 32 and Track 33 outputs are not described as full-corpus
  results;
- rules-as-code bridge outputs are not described as executable policy programs;
- the manuscript states whether each adjacent-dataset workflow is repo-run,
  library-called, API-called, MCP-called, or dataset-consumed;
- Tracks 35-37 outputs are described as planned until their evidence is
  archived;
- CI, Docs, benchmark, and focused protocol tests pass for the publication
  commit.
