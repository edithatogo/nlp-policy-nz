# Broad Legislation Extraction Framework

`nlp-policy-nz` is the producer of source-grounded extraction outputs. Other
projects should consume its manifests rather than importing internal pipeline
objects directly.

Rules-as-code is one extraction family, not the whole framework. The same
manifest shape also covers definitions, obligations, prohibitions, permissions,
powers, conditions, exceptions, eligibility rules, thresholds, dates, entities,
amendments, commencement, repeal, cross-references, penalties, delegations, and
review rights.

## Public Contract

The public schema surface is in `nlp_policy_nz.extraction`:

- `ExtractionRecord` is one extracted legislative fact.
- `SourceTrace` pins the record to a citation path, source URL, retrieved date,
  source SHA256, and source spans.
- `ExtractionManifest` packages records, summaries, known gaps, and trace
  reports for downstream use.
- `ExtractorManifest` describes the extractors that can produce output families.
- `KnownGap` records corpus, parser, extraction, or validation debt as a
  ratchet item.
- `SourceTraceReport` groups records by citation path and source hash for audit
  and stale-output checks.

Manifests are deterministic JSON via `render_extraction_manifest_json()`.
Extractor catalogs are review-friendly YAML via `render_extractor_manifest_yaml()`.

Existing pipeline Parquet outputs can be converted with:

```powershell
nlp-policy-nz export-extractions `
  --parquet output/legislation.parquet `
  --output output/extractions.json `
  --retrieved-at 2026-06-30T00:00:00Z `
  --source-url-base https://example.test/source
```

Batch rules-as-code candidate exports are available through the same
deterministic surface:

```powershell
nlp-policy-nz export-rac-candidates `
  --output-dir output/rac-batch
```

The batch exporter can also consume a stored extraction manifest or a pipeline
Parquet file, while preserving review status and known-gap metadata in the
generated candidate bundle.

For local run tracking and stale-output checks, use the optional SQLite catalog:

```python
from nlp_policy_nz.extraction import (
    list_catalog_runs,
    report_catalog_source_staleness,
    write_manifest_to_catalog,
)

run_id = write_manifest_to_catalog("output/extractions.sqlite", manifest)
runs = list_catalog_runs("output/extractions.sqlite")
staleness = report_catalog_source_staleness(
    "output/extractions.sqlite",
    {"nz/statutes/example-act/2026/10": current_source_text},
)
```

## Source Identity

Downstream consumers should treat source identity as the pair of:

- `citation_path`: a durable NZ citation path, for example
  `nz/statutes/example-act/2026/10`.
- `source_sha256`: the SHA256 of the exact normalized source text used for
  extraction.

`source_url` and `retrieved_at` are provenance fields, not stable identity by
themselves. A changed `source_sha256` means downstream records may be stale even
when the citation path is unchanged.

## Rules-as-Code Handoff

Rules-as-code candidates use `ExtractionFamily.RULES_AS_CODE` and should carry
durable IDs in record attributes when available, for example:

```json
{
  "record_id": "nz:statutes/example-act/2026/10#rules_as_code",
  "family": "rules_as_code",
  "attributes": {
    "rulespec_id": "nz:statutes/example-act/2026/10#obligation"
  }
}
```

The NLP package should export candidate source verification metadata. Executable
RuleSpec content, formula correctness, and runtime evaluation remain downstream
responsibilities.

Track 77 extends that handoff with a batch candidate bundle that keeps
`review_status` and `known_gap_ids` attached to each candidate so fixture or
heuristic outputs remain visibly non-executable.

Track 78 adds the reviewed promotion layer on top of that batch contract. It
keeps the repository-side payload limited to source proof, reviewer evidence,
oracle fixture references, and deterministic JSON/YAML exports. Executable
RuleSpec modules, reviewed formulas, and engine-specific runtime logic remain
downstream in `rulespec-nz`.

Track 79 takes one reviewed commencement domain from that handoff boundary and
turns it into a deterministic PolicyEngine-style package with oracle fixtures
and a repo-local execution harness. It is intentionally narrow and does not
claim whole-corpus executable-law coverage.

## Library Direction

The current baseline is deliberately incremental:

- Pydantic 2 for public schemas and validation.
- `orjson` for fast deterministic JSON export.
- `PyYAML` for extractor catalogs and handoff manifests.
- `pypdf` for official-PDF ingestion fallback when better structured sources
  are unavailable.
- Python stdlib `sqlite3` as the local catalog layer for manifest summaries and
  stale-output audits.

Track 56 covers runtime acceleration decisions. The current policy is documented
in `docs/extraction-runtime.md`: keep Pydantic 2 and `orjson` in the core path,
use Polars/Arrow only for optional table projections, and defer PyO3 or maturin
until profiling identifies a stable Python hot path worth moving.

## Source Inventory Contract

Track 76 adds the fixture-bounded source inventory used to gate "whole NZ
legislation" claims:

- `default_source_inventory_manifest()` loads the checked-in fixture contract
  from `data/track76/source_inventory_fixtures.json`.
- `render_source_inventory_json()` and `render_source_inventory_markdown()`
  produce deterministic review artifacts for the manifest.
- `write_source_inventory_parquet()` exports the same record table to Parquet
  when a Parquet lane is useful in CI or downstream analysis.
- `detect_source_inventory_live_probe_report()` stays opt-in and reports a
  skip on non-Linux runners or GitHub Actions, keeping the default path offline
  and deterministic.

The inventory proves fixture-bounded source readiness only. It does not claim
full-corpus completeness, live crawling, or rights clearance for every NZ
legislation source until a later live collection track closes those gaps.
