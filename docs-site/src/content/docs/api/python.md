---
title: Python API reference
description: Python module reference generated from public docstrings.
---

# Python API reference

This page is generated from module, class, and function docstrings.

## `nlp_policy_nz.api.server`

FastAPI inference server for nlp-policy-nz.

- `Any`: Special type indicating an unconstrained type.
- `BaseModel`: !!! abstract "Usage Documentation"
- `EmbedRequest`: Request body for embedding generation.
- `EmbedResponse`: Embedding generation response body.
- `FastAPI`: `FastAPI` app class, the main entrypoint to use FastAPI.
- `Field`: !!! abstract "Usage Documentation"
- `HTTPException`: An HTTP exception you can raise in your own code to show errors to the client.
- `HealthResponse`: Health check response body.
- `LanguageIdentifier`: Lazy proxy for the language identifier constructor.
- `Path`: PurePath subclass that can make system calls.
- `ProcessRequest`: Request body for inline or file pipeline processing.
- `ProcessResponse`: Pipeline processing response body.
- `SearchRequest`: Request body for semantic search.
- `SearchResponse`: Semantic search response body.
- `create_citation_ruler`: Lazy proxy for the syntactic citation ruler factory.
- `create_nlp_pipeline`: Lazy proxy for the syntactic pipeline factory.
- `embed`: Generate embeddings for one or more input texts.
- `health`: Return API health and lazy model-load state.
- `normalize_text`: Lazy proxy for guard text normalization.
- `process`: Run pipeline processing against a path or inline text.
- `search`: Run semantic vector search over the configured index.
- `search_similar`: Lazy proxy for vector search.

## `nlp_policy_nz.axiom`

Axiom Foundation interoperability helpers for NZ legal NLP.

- `BillAction`: One normalized bill lifecycle action.
- `BillHansardLink`: Candidate link between Hansard debate text and a bill/provision.
- `BillVersion`: Bill version metadata used for Hansard and amendment linkage.
- `RuleSpecReference`: Durable RuleSpec concept reference without runtime coupling.
- `SourceSection`: Paired source text plus metadata before NLP pipeline conversion.
- `SourceSectionMetadata`: Metadata for one authoritative source-section text artifact.
- `StalenessReport`: Non-mutating source hash comparison result.
- `compare_source_staleness`: Compare a stored source hash against current corpus text.
- `make_rulespec_reference`: Create a normalized RuleSpec reference from a corpus citation path.
- `normalise_bill_status`: Map NZ parliamentary status text into a stable lifecycle vocabulary.
- `pipeline_record_rulespec_reference`: Map a pipeline record or NZ provision identifier to a RuleSpec reference.
- `source_section_to_pipeline_record`: Convert a source section into the existing pipeline schema.
- `source_sha256`: Return the SHA-256 hash of exact normalized source text.
- `source_verification_metadata`: Export candidate metadata for a future `rulespec-nz` module.

## `nlp_policy_nz.extraction`

Typed extraction records for source-grounded legislative outputs.

- `CatalogRun`: One extraction manifest run recorded in the local catalog.
- `CatalogStalenessReport`: Non-mutating staleness result for one cataloged source identity.
- `ExtractedSpan`: Character span in normalized source text.
- `ExtractionFamily`: Supported legislation extraction output families.
- `ExtractionManifest`: Portable extraction manifest for downstream consumers.
- `ExtractionRecord`: One normalized extraction from source legislation.
- `ExtractionRunSummary`: Summary counts and coverage signals for an extraction run.
- `ExtractorManifest`: Manifest describing extractors that can produce output families.
- `ExtractorSpec`: Versioned extractor manifest entry for one output family.
- `GapStatus`: Known-gap lifecycle status for extraction ratchets.
- `GapType`: Known-gap categories for broad extraction coverage.
- `KnownGap`: Ratchet item for known extraction coverage or validation debt.
- `SourceTrace`: Checksum-pinned source locator for one extracted record.
- `SourceTraceReport`: Source-to-output audit report for a set of extracted records.
- `export_extraction_manifest_from_parquet`: Load pipeline Parquet rows and write an extraction manifest JSON file.
- `extraction_manifest_from_pipeline_records`: Build a source-grounded extraction manifest from pipeline records.
- `extraction_manifest_from_records`: Build a manifest with deterministic summary fields from records.
- `initialise_extraction_catalog`: Create the extraction catalog schema if needed and return its path.
- `list_catalog_runs`: Return extraction catalog runs in insertion order.
- `render_extraction_manifest_json`: Render an extraction manifest as deterministic JSON.
- `render_extractor_manifest_yaml`: Render an extractor manifest as stable YAML for review and handoff.
- `report_catalog_source_staleness`: Compare cataloged source hashes against current source text.
- `source_trace_reports_from_records`: Build source-to-output trace reports grouped by citation and source hash.
- `write_manifest_to_catalog`: Persist an extraction manifest summary and record source identities.

## `nlp_policy_nz.ontology`

Ontology standards registry, rules-as-code bridge, and helper exports.

- `ControlledConcept`: SKOS-compatible concept record for EuroVoc and local taxonomies.
- `ECLIIdentifier`: Stable ECLI identifier with round-trip parsing support.
- `LegislationProfile`: schema.org/Legislation JSON-LD record.
- `LegislativeResource`: Local ELI/ELI-DL-compatible legislation identifier record.
- `ManifestSummary`: Compact manifest summary used in tests and archive notes.
- `NormSemantics`: Normative semantics inferred from one legal source section.
- `OntologyMappingRecord`: One explicit reviewed mapping between ontology terms.
- `OntologyStandard`: Registry record for one external ontology standard.
- `PolicyEnginePackageSkeleton`: Deterministic package files for a future OpenFisca/PolicyEngine model.
- `PolicyTaxonomy`: Policy-domain classification hook for later SKOS/EuroVoc alignment.
- `RulesAsCodeBridgeRecord`: Deterministic bridge from source law to executable-rule metadata.
- `SourceAnchor`: Stable source text anchor for a rules-as-code bridge record.
- `TemporalValidity`: Temporal validity bounds for a source-grounded rule candidate.
- `add_mapping_record`: Return mappings with a new record appended after duplicate-id checks.
- `build_controlled_concept`: Build a SKOS-compatible JSON-LD concept record.
- `build_ecli_identifier`: Build an ECLI identifier string.
- `build_eli_dl_uri`: Build a deterministic local ELI-DL URI.
- `build_eli_uri`: Build a deterministic local ELI URI.
- `build_eurovoc_concept`: Build a EuroVoc concept record.
- `build_mapping_graph`: Build an RDF graph for explicit ontology mappings.
- `build_mapping_manifest`: Build a deterministic JSON mapping manifest.
- `build_ontology_standards_manifest`: Build the Track 26 standards manifest as a JSON-compatible mapping.
- `build_policyengine_package_skeleton`: Build an offline OpenFisca/PolicyEngine-style package skeleton.
- `build_rules_as_code_bridge`: Build one source-grounded rules-as-code bridge record.
- `build_schema_legislation`: Build a schema.org/Legislation JSON-LD record.
- `concept_key`: Return a stable concept key used by query helpers.
- `dump_ontology_standards_manifest`: Serialise the Track 26 standards manifest to formatted JSON.
- `get_equivalent`: Return explicit equivalent or close target terms for a standard pair.
- `get_ontology_standard`: Return one ontology standard by its stable identifier.
- `load_controlled_concept`: Load a SKOS-compatible concept record from JSON.
- `load_mapping_manifest`: Load and validate mapping records from a JSON manifest.
- `load_ontology_standards_manifest`: Load the checked-in standards manifest.
- `load_schema_legislation`: Load a schema.org/Legislation JSON-LD record from JSON.
- `mapping_json_schema`: Return the JSON Schema for mapping manifests.
- `mapping_summary`: Return summary statistics for a mapping set.
- `mappings_by_standard_pair`: Return mappings from one standard to another.
- `ontology_standard_ids`: Return the registry identifiers in stable sorted order.
- `ontology_standard_mappings`: Return stable ontology identifiers mapped to local namespaces.
- `parse_ecli_identifier`: Parse an ECLI identifier string back to structured data.
- `parse_eli_uri`: Parse an ELI or ELI-DL URI back to a local legislation record.
- `parse_schema_legislation`: Parse a schema.org/Legislation JSON-LD record.
- `remove_mapping_record`: Return mappings with ``mapping_id`` removed.
- `render_mermaid_graph`: Render a Mermaid graph for standards-level ontology relationships.
- `render_rules_as_code_bridge_json`: Render a bridge record as stable formatted JSON.
- `replace_mapping_record`: Return mappings with one existing record replaced by ``record``.
- `repo_root`: Return the repository root for this package.
- `traverse_mappings`: Traverse explicit mappings from a concept up to ``max_hops``.
- `update_mapping_review_status`: Return mappings with one record's review status changed.
- `validate_mapping_manifest`: Validate a mapping manifest and return records.
- `write_mapping_artifacts`: Write JSON, RDF, JSON-LD, summary, schema, and Mermaid artifacts.
- `write_ontology_standards_manifest`: Write the deterministic Track 26 manifest to disk.
- `write_policyengine_package_skeleton`: Write a package skeleton to *output_dir* and return the directory path.
- `write_rules_as_code_bridge_json`: Write a bridge record to disk and return the output path.

## `nlp_policy_nz.storage`

Storage Module.

- `HaystackRAGPipeline`: Orchestrate embedding-based retrieval with a Haystack-compatible interface.
- `LanceDBAdapter`: A vector index backed by a LanceDB table.
- `PipelineRecord`: A single processed document record flowing through the NLP pipeline.
- `VectorBackend`: Abstract vector-store backend.
- `load_from_parquet`: Load pipeline records from a Parquet file on disk.
- `records_to_dataframe`: Convert a sequence of pipeline records to a Narwhals-compatible DataFrame.
- `serialize_to_parquet`: Serialize pipeline records to a Parquet file on disk.

## `nlp_policy_nz.telemetry`

OpenTelemetry helpers for the NLP policy pipeline.

- `BenchmarkEvidenceContract`: Stable metadata for repo-side pipeline benchmark evidence.
- `TelemetryHandle`: Result returned by tracing configuration.
- `TraceConfig`: Configuration for OpenTelemetry tracing exporters.
- `Track19EvidenceReport`: Measured evidence for Track 19 acceptance criteria.
- `configure_tracing`: Configure OpenTelemetry tracing for pipeline runs.
- `evaluate_track19_acceptance`: Evaluate Track 19 gates without overclaiming local micro-benchmarks.
- `pipeline_span`: Start a named pipeline span when OpenTelemetry is available.
- `record_span_exception`: Record an exception on the current active span when tracing is active.
- `render_track19_evidence_markdown`: Render a concise Track 19 evidence summary for conductor notes.
- `set_span_attribute`: Set an attribute on the current active span when tracing is active.
- `track19_residual_external_gates`: Return pending full-corpus and dependency gates.
