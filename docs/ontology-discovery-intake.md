# Ontology Discovery and Intake

Track 28 records additional ontology, vocabulary, schema, and rules-as-code
candidates for later mapping and implementation.

The checked artifacts are:

- `data/ontologies/track28_discovery_log.json`: reviewed candidates with source,
  authority, license, version, relevance, risk, scores, and decision.
- `data/ontologies/track28_triage.json`: ranked candidates and decision counts.
- `data/ontologies/track28_standards_registry_addendum.json`: approved
  implement/map-only candidates in the Track 26 registry shape.
- `data/ontologies/track28_blockers.json`: implementation blockers for
  non-rejected candidates.

## Intake Decisions

Candidates are triaged as:

- `implement`: add to the registry addendum and plan a repo-side implementation.
- `map-only`: add as an interoperability target without a core implementation.
- `monitor`: keep as a design reference or future research candidate.
- `reject`: do not add until a concrete use case or authoritative source exists.

The current high-value additions are W3C OWL 2, RDF 1.2, SHACL, NZGLS,
data.govt.nz dataset metadata, and NZ Legislation Guidelines concepts.

ODRL, AGLS, and Catala are useful map-only targets. SOSA/SSN, Docassemble, and
legal-informatics literature patterns are monitor items. FIGI, ErgoAI, and the
unverified STOICA reference are rejected for the core registry.

## Scoring

Each candidate receives 1-5 scores for:

- authority;
- New Zealand relevance;
- interoperability;
- license and access;
- maintenance status.

The total score is used for deterministic ranking. A high score does not by
itself imply implementation: candidates must also have a suitable scope,
license/access posture, and source-data path.

## Registry Relationship

Track 28 does not rewrite Track 26. It creates an addendum so Track 29 and Track
30 can decide exact mapping and inference work without losing the provenance of
why a candidate was accepted, monitored, or rejected.
