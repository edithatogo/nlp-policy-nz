# Track 54 Evidence

## Local Verification

The Axiom interoperability helpers are verified offline:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_rac_bridge.py tests\test_axiom_integration.py
.\.venv\Scripts\python.exe -m ruff check src\nlp_policy_nz\axiom\rulespec.py tests\test_rac_bridge.py tests\test_axiom_integration.py
```

Latest result: 9 tests passed and Ruff passed.

The repository-wide quality gate was also run after the RuleSpec metadata
compatibility adjustments:

```powershell
& 'C:\Users\60217257\.pixi\bin\pixi.exe' run check
```

Latest result: Ruff, Vale, Ruff format, complexity, Tach, and pytest passed;
pytest reported 666 passed, 1 skipped, and 3 third-party deprecation warnings.

Track 54's Conductor registration and offline-boundary claims are protected by
a focused regression test:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_track54_axiom_conductor.py tests\test_axiom_integration.py tests\test_rac_bridge.py
.\.venv\Scripts\python.exe -m ruff check tests\test_track54_axiom_conductor.py tests\test_axiom_integration.py tests\test_rac_bridge.py
```

Latest result: 14 tests passed and Ruff passed.

The focused tests include guards for:

- keeping public `DocumentType` and `BillStatus` aliases importable from
  `nlp_policy_nz.axiom`;
- keeping public `DOCUMENT_TYPES` and `BILL_STATUSES` vocabularies importable
  for downstream validation and typing;
- validating direct `SourceSectionMetadata` construction for required source
  identity fields and lowercase SHA-256 checksum pins;
- serializing staleness reports through `to_dict()`;
- rejecting out-of-range bill/Hansard linkage confidence scores;
- validating direct bill action, bill version, and Hansard link construction
  for required identity fields, normalized statuses, and checksum pins;
- enforcing the Axiom document-type vocabulary at `SourceSection` construction
  and in the `rac-export --document-type` CLI choices;
- rejecting empty normalized RuleSpec path or concept fragments;
- normalizing and validating direct `RuleSpecReference` construction to match
  factory-created durable IDs;
- validating direct rules-as-code bridge source anchors and taxonomy records
  before JSON-LD export;
- validating direct bridge records for a required
  `rulespec.rulespec_reference.durable_id` before JSON-LD rendering;
- rejecting absolute or parent-traversal file paths in direct
  PolicyEngine/OpenFisca package skeleton manifests before writing files;
- validating direct PolicyEngine/OpenFisca package skeleton manifests for
  package identity, source citation, RuleSpec ID, and text file content;
- keeping generated PolicyEngine/OpenFisca placeholder variable names valid
  when source concepts collide with Python keywords;
- preventing legacy `source_url` fields from reappearing under
  `module.source_verification`.

The Axiom relevance note is linked from the README documentation section, and
the note itself passes the repository Vale configuration:

```powershell
& 'C:\Users\60217257\.pixi\bin\pixi.exe' run vale docs/axiom-foundation-relevance.md
```

Latest result: 0 errors and 0 warnings.

The `pixi.toml` lint task now includes `docs/axiom-foundation-relevance.md` in
its Vale file list. The scoped Vale command for the lint-task documentation set
passes:

```powershell
& 'C:\Users\60217257\.pixi\bin\pixi.exe' run vale docs/build_backend.md docs/pydantic_vs_msgspec.md docs/axiom-foundation-relevance.md
```

Latest result: 0 errors and 0 warnings. A full `pixi run lint` attempt still
stops in unrelated Ruff findings in existing `universal_framework*`,
`xml_parser.py`, and profiling script files before the Vale step.

The README also includes an offline `rac-export` example, and the CLI parser
has a regression test proving the subcommand remains registered with RuleSpec
bridge help text:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q tests\test_cli.py::TestArgumentParser::test_parser_has_rac_export_subcommand tests\test_rac_bridge.py tests\test_track54_axiom_conductor.py
.\.venv\Scripts\python.exe -m ruff check tests\test_cli.py
```

Latest result: 10 tests passed and Ruff passed.

Track 54 also has a dependency-boundary regression that checks `pyproject.toml`
and `pixi.toml` do not add Axiom repositories, `rulespec-nz`, or
`axiom-rules-engine` as package dependencies. This keeps the integration as
selective code and convention reuse rather than runtime vendoring.

The documentation and Conductor spec now state the producer/consumer boundary:
`nlp-policy-nz` remains the independent producer of source-grounded NLP,
provenance, benchmark, and publication outputs; downstream projects consume
those outputs for executable RuleSpec, oracle, microsimulation, or UI work.

## rulespec-nz Compatibility Review

The bridge output was checked against the adjacent `rulespec-nz` repository:

```powershell
& 'C:\Users\60217257\.pixi\bin\pixi.exe' run pytest tests/test_repository_layout.py -q
```

Latest result in `rulespec-nz`: 13 tests passed.

The compatibility decision is:

- `module.source_verification` uses `corpus_citation_path` or
  `corpus_citation_paths` as the RuleSpec source locator.
- Raw URL, retrieval timestamp, and checksum pins are kept in adjacent
  provenance metadata.
- The bridge does not emit legacy RuleSpec YAML fields such as
  `module.source_verification.source_url`.
- Executable RuleSpec content still belongs in `rulespec-nz`; this repository
  exports source-grounded candidates only.
