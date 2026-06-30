# Track 28 Evidence

## Ontology Discovery and Intake

Track 28 is implemented as deterministic discovery and intake artifacts:

- `src/nlp_policy_nz/quality/track28_ontology_discovery.py` contains the
  reviewed candidate list, scoring model, triage decisions, registry addendum
  builder, blocker builder, and artifact writer.
- `data/ontologies/track28_discovery_log.json` records source, version, license,
  authority, relevance, risk, scores, implementation effort, and triage decision
  for each candidate.
- `data/ontologies/track28_triage.json` ranks candidates and records decision
  counts.
- `data/ontologies/track28_standards_registry_addendum.json` adds approved
  implement/map-only candidates in the Track 26 registry shape.
- `data/ontologies/track28_blockers.json` records data, specification, and
  integration blockers for non-rejected candidates.
- `docs/ontology-discovery-intake.md` explains the intake model and relationship
  to Track 26, Track 29, and Track 30.

## Coverage

The discovery log covers:

- official standards bodies and public vocabulary registries;
- New Zealand and adjacent government metadata standards;
- legal-informatics literature sources;
- rules-as-code tooling; and
- graph/vector/publication standards.

High-value implement decisions include OWL 2, RDF 1.2, SHACL, NZGLS,
data.govt.nz dataset metadata, and NZ Legislation Guidelines concepts.
Map-only decisions include ODRL, AGLS, and Catala. Monitor and reject decisions
are explicitly recorded to avoid silent scope creep.

## Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track28_ontology_discovery.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\quality\track28_ontology_discovery.py tests\test_track28_ontology_discovery.py
```

Latest result: 5 tests passed and Ruff passed.

## Conductor and Registry Verification

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\quality\track28_ontology_discovery.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py
```

Latest result: 13 tests passed and Ruff passed.

## Broader Focused Validation

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\quality\track28_ontology_discovery.py src\nlp_policy_nz\extraction src\nlp_policy_nz\axiom src\nlp_policy_nz\ontology\rac_bridge.py src\nlp_policy_nz\cli\main.py scripts\benchmark_extraction_manifest_runtime.py tests\test_track28_ontology_discovery.py tests\test_track28_conductor.py tests\test_track26_standards_registry.py tests\test_track55_56_conductor.py tests\test_track56_extraction_runtime.py tests\test_extraction_catalog.py tests\test_extraction_exporter.py tests\test_extraction_schemas.py tests\test_axiom_integration.py tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
```

Latest result: 50 tests passed and Ruff passed.
