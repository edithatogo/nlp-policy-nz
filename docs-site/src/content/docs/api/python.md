---
title: Python API reference
description: Python module reference generated from public docstrings.
---

# Python API reference

This page is generated from module, class, and function docstrings.

## `nlp_policy_nz.api.server`

FastAPI inference server for nlp-policy-nz.

- `APIKeyStore`: JSON-backed key store for API authentication.
- `Any`: Special type indicating an unconstrained type.
- `AuthContext`: Authenticated request context.
- `BaseModel`: !!! abstract "Usage Documentation"
- `EmbedRequest`: Request body for embedding generation.
- `EmbedResponse`: Embedding generation response body.
- `EndpointContract`: Describe one public HTTP contract surface for the API.
- `FastAPI`: `FastAPI` app class, the main entrypoint to use FastAPI.
- `Field`: !!! abstract "Usage Documentation"
- `HTTPException`: An HTTP exception you can raise in your own code to show errors to the client.
- `HealthResponse`: Health check response body.
- `LanguageIdentifier`: Lazy proxy for the language identifier constructor.
- `Path`: PurePath subclass that can make system calls.
- `ProbeResponse`: Health probe response body.
- `ProblemCode`: Standardized API error codes.
- `ProblemDetail`: RFC 7807 problem detail payload with an API-specific error code.
- `ProblemError`: Field-level validation error payload.
- `ProcessRequest`: Request body for inline or file pipeline processing.
- `ProcessResponse`: Pipeline processing response body.
- `Request`: A base class for incoming HTTP connections, that is used to provide
- `SearchRequest`: Request body for semantic search.
- `SearchResponse`: Semantic search response body.
- `VersionResponse`: Version metadata response body.
- `api_contract_summary`: Return a compact summary for docs and drift checks.
- `api_endpoint_inventory`: Return the public HTTP endpoint inventory as JSON-ready data.
- `build_audit_logger`: Return a logger that appends JSON audit events to a rotating log.
- `config_hash`: Return a deterministic config hash for startup diagnostics.
- `create_citation_ruler`: Lazy proxy for the syntactic citation ruler factory.
- `create_nlp_pipeline`: Lazy proxy for the syntactic pipeline factory.
- `current_request_id`: Return the active request id, if one is set.
- `dataclass`: Add dunder methods based on the fields defined in the class.
- `datetime`: datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])
- `decrement_active_requests`: Decrement the active request gauge.
- `defaultdict`: defaultdict(default_factory=None, /, [...]) --> dict with default factory
- `deque`: A list-like sequence optimized for data accesses near its endpoints.
- `embed`: Generate embeddings for one or more input texts.
- `emit_audit_event`: Write a structured audit event.
- `extract_api_key`: Extract an API key from Authorization or X-API-Key headers.
- `generate_request_id`: Generate a stable request identifier.
- `get_structured_logger`: Return a logger that emits JSON records to stderr.
- `health`: Return API health and lazy model-load state.
- `increment_active_requests`: Increment the active request gauge.
- `liveness_probe`: Report basic process liveness.
- `load_feature_flags`: Load feature flags from environment variables.
- `load_runtime_settings`: Load runtime settings from environment variables.
- `load_security_settings`: Load security settings from environment variables.
- `metrics`: Expose Prometheus-compatible metrics.
- `normalize_text`: Lazy proxy for guard text normalization.
- `observability_middleware`: Apply request IDs, auth, rate limiting, metrics, and audit logging.
- `problem_response`: Build a problem+json response.
- `process`: Run pipeline processing against a path or inline text.
- `readiness_probe`: Report whether the pipeline and database are ready to serve.
- `record_request`: Record a completed request.
- `register_problem_handlers`: Register RFC 7807 exception handlers on the FastAPI app.
- `render_metrics`: Render the in-memory metrics in Prometheus exposition format.
- `required_scope_for_path`: Return the required scope for a request path, if any.
- `reset_metrics`: Reset all metrics for test isolation.
- `reset_request_id`: Reset the active request id using a token returned from set_request_id.
- `search`: Run semantic vector search over the configured index.
- `search_similar`: Lazy proxy for vector search.
- `set_model_loaded`: Set the model-load gauge.
- `set_request_id`: Set the active request id for the current context.
- `startup_probe`: Report whether the model has finished startup initialization.
- `timedelta`: Difference between two datetime values.
- `verify_api_key`: Validate an API key against the store and required scope.
- `version`: Return the canonical release version metadata.
- `versioned_openapi_v1`: Return the versioned OpenAPI document for v1 clients.
- `versioned_openapi_v2`: Return the versioned OpenAPI document for v2 clients.

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

- `AccessClass`: Access boundary used by Hathi-NZ publication routing.
- `AcquisitionMode`: Permitted source acquisition route.
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
- `HathiArchiveItem`: One source item with rights, provenance, and publication routing.
- `HathiArchiveRegistry`: Validated collection-level registry summary and dataset descriptors.
- `HathiDatasetDescriptor`: A publication dataset registered in the Hathi-NZ collection.
- `HathiWorkItem`: Cloud work item derived from a validated archive item.
- `HathiWorkManifest`: Resumable work plan that contains metadata, not corpus payloads.
- `HathiWorkShard`: Deterministic shard of cloud work item identities.
- `KnownGap`: Ratchet item for known extraction coverage or validation debt.
- `PublicationDecision`: Maximum content publication decision for one source item.
- `RulesAsCodeCandidateBundle`: Deterministic candidate export bundle for rules-as-code handoff.
- `SourceInventoryKnownGap`: Known inventory gap or retrieval blocker.
- `SourceInventoryLiveProbeReport`: Report describing whether the optional live probe ran.
- `SourceInventoryManifest`: Deterministic legislation source inventory for rules-as-code planning.
- `SourceInventoryRecord`: One durable source-location record in the legislation inventory.
- `SourceInventorySummary`: Stable summary counts for a source inventory manifest.
- `SourceTrace`: Checksum-pinned source locator for one extracted record.
- `SourceTraceReport`: Source-to-output audit report for a set of extracted records.
- `build_rules_as_code_candidate_bundle_from_extraction_manifest`: Build a batch candidate export from a broad extraction manifest.
- `build_rules_as_code_candidate_bundle_from_pipeline_parquet`: Build a batch candidate export from pipeline Parquet output.
- `build_rules_as_code_candidate_bundle_from_source_inventory`: Build a batch candidate export from the fixture-bounded inventory.
- `build_source_inventory_rows`: Return a flat row set that can be written to Parquet.
- `build_work_manifest`: Build a stable cloud work manifest from validated item rows.
- `default_source_inventory_manifest`: Build the default inventory manifest from checked-in fixture metadata.
- `detect_source_inventory_live_probe_report`: Report whether the optional live inventory probe is eligible to run.
- `export_extraction_manifest_from_parquet`: Load pipeline Parquet rows and write an extraction manifest JSON file.
- `export_rules_as_code_candidates_from_extraction_manifest`: Build and write candidate artifacts from a stored extraction manifest.
- `export_rules_as_code_candidates_from_pipeline_parquet`: Build and write candidate artifacts from pipeline Parquet rows.
- `export_rules_as_code_candidates_from_source_inventory`: Build and write candidate artifacts from the fixture inventory.
- `extraction_manifest_from_pipeline_records`: Build a source-grounded extraction manifest from pipeline records.
- `extraction_manifest_from_records`: Build a manifest with deterministic summary fields from records.
- `initialise_extraction_catalog`: Create the extraction catalog schema if needed and return its path.
- `list_catalog_runs`: Return extraction catalog runs in insertion order.
- `load_archive_registry`: Load the Hathi-NZ registry projection without acquiring corpus data.
- `load_extraction_manifest_json`: Load an extraction manifest from deterministic JSON.
- `load_source_inventory_manifest_json`: Load a source inventory manifest from deterministic JSON.
- `render_extraction_manifest_json`: Render an extraction manifest as deterministic JSON.
- `render_extractor_manifest_yaml`: Render an extractor manifest as stable YAML for review and handoff.
- `render_hathi_json_schema`: Return the versioned JSON Schema for the Hathi ingestion contract.
- `render_source_inventory_json`: Render the inventory manifest as deterministic JSON.
- `render_source_inventory_markdown`: Render a concise markdown evidence summary for the inventory.
- `render_work_manifest_json`: Render a deterministic JSON work manifest.
- `report_catalog_source_staleness`: Compare cataloged source hashes against current source text.
- `source_trace_reports_from_records`: Build source-to-output trace reports grouped by citation and source hash.
- `validate_curated_seed_count`: Fail closed when a curated seed cohort changes unexpectedly.
- `validate_source_inventory_manifest`: Return whether the manifest is structurally valid and gap-complete.
- `write_manifest_to_catalog`: Persist an extraction manifest summary and record source identities.
- `write_rules_as_code_candidate_bundle`: Write the batch candidate export artifacts to *output_dir*.
- `write_source_inventory_artifacts`: Write the standard Track 76 artifact bundle to disk.
- `write_source_inventory_parquet`: Write the source inventory as a deterministic Parquet table.

## `nlp_policy_nz.ontology`

Ontology standards registry, rules-as-code bridge, and helper exports.

- `ControlledConcept`: SKOS-compatible concept record for EuroVoc and local taxonomies.
- `CorpusEvidence`: A local evidence pointer used to justify a concept candidate.
- `ECLIIdentifier`: Stable ECLI identifier with round-trip parsing support.
- `EngineAdapterContract`: Support-level metadata for one downstream rules engine.
- `InferredMappingCandidate`: A non-authoritative mapping candidate that must be reviewed before use.
- `LegislationProfile`: schema.org/Legislation JSON-LD record.
- `LegislativeResource`: Local ELI/ELI-DL-compatible legislation identifier record.
- `ManifestSummary`: Compact manifest summary used in tests and archive notes.
- `MultiEngineParityBundle`: All Track 80 artifacts derived from the reviewed pilot domain.
- `MultiEngineParityCase`: Deterministic parity result for one oracle case.
- `MultiEngineParityReport`: Deterministic parity report across the repo-local engine contracts.
- `NZOntologyBundle`: The Track 31 ontology induction output bundle.
- `NZOntologyConcept`: A New Zealand-specific ontology class, property, or vocabulary concept.
- `NormSemantics`: Normative semantics inferred from one legal source section.
- `OntologyAnchor`: An upstream ontology anchor for a NZ concept candidate.
- `OntologyMappingRecord`: One explicit reviewed mapping between ontology terms.
- `OntologyStandard`: Registry record for one external ontology standard.
- `OntologyTerm`: A compact ontology term used by deterministic mapping inference.
- `PolicyEnginePackageSkeleton`: Deterministic package files for a future OpenFisca/PolicyEngine model.
- `PolicyTaxonomy`: Policy-domain classification hook for later SKOS/EuroVoc alignment.
- `RulesAsCodeBridgeRecord`: Deterministic bridge from source law to executable-rule metadata.
- `SKOSConcept`: A concept in a Track 31 controlled vocabulary scheme.
- `SKOSConceptScheme`: A deterministic NZ controlled vocabulary scheme.
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
- `build_multi_engine_parity_bundle`: Build the Track 80 parity bundle from a reviewed pilot domain.
- `build_nz_ontology_bundle`: Build the deterministic Track 31 NZ ontology candidate bundle.
- `build_nz_ontology_graph`: Build an RDF graph for NZ ontology candidates and SKOS schemes.
- `build_ontology_standards_manifest`: Build the Track 26 standards manifest as a JSON-compatible mapping.
- `build_openfisca_package_skeleton`: Build an offline OpenFisca-style package skeleton.
- `build_policyengine_package_skeleton`: Build an offline PolicyEngine-style package skeleton.
- `build_rules_as_code_bridge`: Build one source-grounded rules-as-code bridge record.
- `build_schema_legislation`: Build a schema.org/Legislation JSON-LD record.
- `build_skos_concept_schemes`: Build controlled vocabularies for NZ ontology publication surfaces.
- `concept_key`: Return a stable concept key used by query helpers.
- `dump_ontology_standards_manifest`: Serialise the Track 26 standards manifest to formatted JSON.
- `get_equivalent`: Return explicit equivalent or close target terms for a standard pair.
- `get_ontology_standard`: Return one ontology standard by its stable identifier.
- `infer_embedding_matches`: Infer candidates from supplied or injected term embedding vectors.
- `infer_exact_matches`: Infer candidates from exact normalized labels or aliases.
- `infer_fuzzy_matches`: Infer close-match candidates from normalized label and definition similarity.
- `infer_mapping_candidates`: Run deterministic inference methods and merge duplicate candidates.
- `infer_structural_matches`: Infer candidates from overlapping parent or child neighbourhood labels.
- `infer_synonym_matches`: Infer candidates when terms share a supplied synonym group.
- `infer_triangulated_matches`: Infer candidates by triangulating through reviewed third-party mappings.
- `llm_interpretation_prompt_schema`: Return the required structured output schema for optional LLM review.
- `load_controlled_concept`: Load a SKOS-compatible concept record from JSON.
- `load_mapping_manifest`: Load and validate mapping records from a JSON manifest.
- `load_ontology_standards_manifest`: Load the checked-in standards manifest.
- `load_schema_legislation`: Load a schema.org/Legislation JSON-LD record from JSON.
- `load_track80_domain_json`: Load the Track 79 reviewed pilot domain used by Track 80 parity checks.
- `mapping_json_schema`: Return the JSON Schema for mapping manifests.
- `mapping_summary`: Return summary statistics for a mapping set.
- `mappings_by_standard_pair`: Return mappings from one standard to another.
- `merge_inferred_candidates`: Merge duplicate source-target candidates and boost confidence by agreement.
- `normalize_mapping_text`: Normalize labels and aliases for deterministic comparison.
- `ontology_standard_ids`: Return the registry identifiers in stable sorted order.
- `ontology_standard_mappings`: Return stable ontology identifiers mapped to local namespaces.
- `parse_ecli_identifier`: Parse an ECLI identifier string back to structured data.
- `parse_eli_uri`: Parse an ELI or ELI-DL URI back to a local legislation record.
- `parse_schema_legislation`: Parse a schema.org/Legislation JSON-LD record.
- `remove_mapping_record`: Return mappings with ``mapping_id`` removed.
- `render_mermaid_graph`: Render a Mermaid graph for standards-level ontology relationships.
- `render_multi_engine_parity_report_json`: Render the parity report as stable formatted JSON.
- `render_multi_engine_parity_report_markdown`: Render the parity report as a compact Markdown summary.
- `render_rules_as_code_bridge_json`: Render a bridge record as stable formatted JSON.
- `replace_mapping_record`: Return mappings with one existing record replaced by ``record``.
- `repo_root`: Return the repository root for this package.
- `slugify_mapping_token`: Return a filesystem and identifier friendly token.
- `traverse_mappings`: Traverse explicit mappings from a concept up to ``max_hops``.
- `update_mapping_review_status`: Return mappings with one record's review status changed.
- `validate_mapping_manifest`: Validate a mapping manifest and return records.
- `validate_nz_ontology_bundle`: Validate Track 31 candidate consistency.
- `write_inferred_mapping_manifest`: Write a deterministic review queue for inferred mapping candidates.
- `write_llm_interpretation_prompt`: Write the optional LLM interpretation prompt contract to disk.
- `write_mapping_artifacts`: Write JSON, RDF, JSON-LD, summary, schema, and Mermaid artifacts.
- `write_multi_engine_parity_bundle`: Write the Track 80 bundle and return the resolved output directory.
- `write_nz_ontology_artifacts`: Write Track 31 JSON, Turtle, JSON-LD, and SKOS artifacts.
- `write_ontology_standards_manifest`: Write the deterministic Track 26 manifest to disk.
- `write_policyengine_package_skeleton`: Write a package skeleton to *output_dir* and return the directory path.
- `write_rules_as_code_bridge_json`: Write a bridge record to disk and return the output path.
- `write_track30_inference_artifacts`: Write deterministic Track 30 candidate and prompt artifacts.

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

