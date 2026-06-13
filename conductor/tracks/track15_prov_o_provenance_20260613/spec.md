# Track 15: PROV-O Provenance Ontology for Pipeline Traces

**Dependencies**: Track 6 (Storage Layer), Track 9 (Zenodo)
**Parallelization Node**: Provenance & Reproducibility
**Status**: Pending

---

## Goal

Implement PROV-O-compatible provenance tracking for every pipeline processing run. Record which pipeline version, model version, parameters, and timestamps produced each dataset, and link outputs to Zenodo DOIs as provenance records. Enables full reproducibility of NLP corpora.

## Scope

### What This Track Covers

1. **Provenance Recorder**: A module that captures pipeline execution context: commit SHA, model versions (`model_loader` state), parameters, start/end timestamps.
2. **PROV-O Serializer**: Export provenance as PROV-O compliant JSON-LD (entities = datasets, activities = pipeline runs, agents = software/system).
3. **Provenance File**: Sidecar `.prov.json` file alongside each Parquet output with full provenance trace.
4. **Zenodo Provenance Link**: Record provenance in Zenodo deposit metadata (software version, model card).
5. **CLI Query**: `nlp-policy-nz provenance <parquet_path>` subcommand to inspect provenance.

### What This Track Does NOT Cover

- Real-time tracing (OpenTelemetry — Track 19)
- Dataset-level DCAT metadata (can be linked)

## Ontologies & Standards

- **W3C PROV-O**: Core provenance ontology (Entity, Activity, Agent)
- **PROV-DM**: Data model for provenance interchange

## Acceptance Criteria

- [ ] Provenance recorder captures pipeline version, model version, parameters, timestamps
- [ ] PROV-O JSON-LD export is valid against PROV-O schema
- [ ] Sidecar `.prov.json` file created for each Parquet output
- [ ] `provenance` CLI subcommand displays provenance info
- [ ] Zenodo deposit includes provenance metadata
- [ ] Test coverage > 90%
