# Track 11: Temporal Expression Extraction & Time Ontology

**Dependencies**: Track 4 (Syntactic Layer), Track 5 (Semantic Layer)
**Parallelization Node**: Temporal Analysis
**Status**: Pending

---

## Goal

Extract, normalize, and classify temporal expressions from NZ legislation and Hansard — including effective dates, commencement dates, deadlines, durations, and periodic references. Annotate using a TimeML-inspired scheme and model temporal relationships between legal events.

## Scope

### What This Track Covers

1. **Temporal Expression Extractor**: spaCy component identifying date/time expressions ("1 July 2024", "within 28 days", "commencing on") using regex and rule-based patterns.
2. **TimeML-Inspired Annotation**: TIMEX3-style tags with type (DATE, TIME, DURATION, SET) and normalized ISO values.
3. **Temporal Relationship Graph**: NetworkX-based graph linking temporal expressions to legal events (sections, amendments, commencement).
4. **PipelineRecord Enrichment**: Add `temporal_expressions: list[dict]` to the record schema.

### What This Track Does NOT Cover

- Deontic modality (Track 10)
- Coreference resolution

## Ontologies & Standards

- **TimeML / ISO 24617-1**: TIMEX3, SIGNAL, EVENT tags
- **OWL-Time**: W3C OWL ontology for temporal relationships
- **ISO 8601**: Normalized date/time representation

## Acceptance Criteria

- [ ] Temporal extractor identifies DATE, TIME, DURATION, SET expressions
- [ ] Normalized ISO 8601 values produced for each expression
- [ ] Temporal relationship graph links dates to sections/events
- [ ] PipelineRecord includes `temporal_expressions` field
- [ ] Parquet output contains temporal annotations
- [ ] Test coverage > 90%
