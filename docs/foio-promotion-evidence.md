# FOI-O Promotion Evidence

Track 79/80 and the FOI-O adapters provide deterministic candidate bundles and
diagnostic metrics. They do not, by themselves, establish empirical legal-label
promotion evidence.

`data/foio/promotion_evidence_manifest.json` is the current owner-controlled
handoff. It intentionally contains no source records, hashes, model revisions,
or reviewer identities because the repository does not yet have rights-cleared
held-out FOI-O evidence for NZ, Commonwealth, or NSW.

The `foio_promotion` contract requires, independently for each jurisdiction:

- immutable archive, legal-source, ontology, model, pipeline, and rights identities;
- a disjoint held-out split identified by real record IDs;
- affirmative rights clearance for evaluation and derived metrics;
- reviewer identities, completed adjudication, and a deterministic evaluation report.

Until all gates pass, the report status is `blocked` and no promotion decision
is emitted. Existing repeated-character fixture hashes and example URLs are
diagnostic placeholders and are rejected by the promotion gate.
