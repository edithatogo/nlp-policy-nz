# Haystack Sovereign Deploy Checklist

Track 99 air-gap and onshore deployment checklist for optional Haystack governance orchestration. Use alongside `docs/haystack-governance-decision.md`.

Parent issue: [#189](https://github.com/edithatogo/nlp-policy-nz/issues/189)

## Pre-deploy

- [ ] Pin model artifact digests (HF revision SHA or local tarball hash) in deployment config.
- [ ] Pre-populate local Hugging Face cache on the onshore host; block outbound model downloads at runtime.
- [ ] Confirm LanceDB data directory resides on onshore storage with access controls.
- [ ] Block telemetry and vendor egress (disable OTLP exporters, Haystack telemetry, and cloud callbacks).
- [ ] Set `GENERATIVE_DEFAULT_ALLOWED = False` and verify restricted pipelines exclude generator components.
- [ ] Attach sovereignty meta tags on ingest: `access_class`, `rights_cleared`, `jurisdiction`, `sovereign_host`.
- [ ] Enable PROV-O dual-write: component step metadata flows to `ProvenanceRecorder` and `.prov.json` sidecars.

## Runtime verification

- [ ] `import nlp_policy_nz` does not load `haystack` modules on the default path.
- [ ] Indexing pipeline runs offline with in-memory or LanceDB writers only.
- [ ] Extractive QA answers are verbatim substrings with document offsets.
- [ ] Evaluation scorecards set `faithfulness_evaluator_authoritative: false` and `promotion_allowed: false`.
- [ ] Restricted/sovereign documents fail closed at the rights gate without explicit clearance.

## Post-deploy audit

- [ ] Record pinned digests, cache paths, and LanceDB URI in the deployment evidence bundle.
- [ ] Confirm no raw restricted corpora left default CLI or publication paths.
- [ ] Archive scorecards and PROV-O sidecars for governance review — not for automatic promotion.

## No-promotion reminder

Sovereign deploy readiness does not imply publication approval. Human review and existing `PipelineRecord` / publication protocol gates remain mandatory.
