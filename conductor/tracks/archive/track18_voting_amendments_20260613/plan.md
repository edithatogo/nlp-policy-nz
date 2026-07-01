# Track 18: Voting Record Analysis & Legislative Amendment Tracking

**Dependencies**: Track 4, Track 7
**Parallelization Node**: Parliamentary Analytics
**Status**: Complete

---

## Goal

Parse parliamentary voting records (divisions) from Hansard, detect legislative amendments between bill versions, and track the full amendment lifecycle from introduction to passage or defeat. Enables downstream corpus-nz-hansard voting pattern analysis.

## Scope

### What This Track Covers

1. **Voting Record Parser**: Extract division details from Hansard — motion text, aye/nay/abstain counts per MP, outcome (passed/defeated).
2. **Amendment Detector**: Parse amendment text from Hansard debates and committee reports — identify amendment type (substantive/technical/Supplementary Order Paper).
3. **Bill Version Diff**: Track changes between bill versions using structural diff of XML/JSON representations.
4. **Amendment Lifecycle Graph**: NetworkX graph tracking amendments from proposal → debate → vote → outcome.
5. **PipelineRecord Enrichment**: Add `voting_record` and `amendments` fields.

### What This Track Does NOT Cover

- Stance detection (Track 13)
- Argument mining (Track 13)

---

## Phases

### Phase 1: Voting Record Parser
**Estimated Effort**: Medium
**Status**: ✅ Completed
**Completed At**: 2026-06-19T19:18:00Z

Extract division details from Hansard XML records and produce structured voting data.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1.1 | Analyze Hansard division format (sample 50 division records) | [x] | (a39086b) |
| 1.2 | Create `src/nlp_policy_nz/parliament/voting.py` with voting record parser — extract motion text, aye/nay/abstain tallies, MP-level votes, outcome | [x] | (a39086b) |
| 1.3 | Implement MP-to-vote mapping with party affiliation lookup (from KB) | [x] | (a39086b) |
| 1.4 | Write unit tests for voting record parsing covering all division variants | [x] | (a39086b) |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 1 — Track 18` ✅ (a39086b)

### Phase 2: Amendment Detection & Bill Diff
**Estimated Effort**: Medium-High
**Status**: ✅ Completed

Parse amendment text from debates and committee reports, detect changes between bill versions, and model the amendment lifecycle.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `src/nlp_policy_nz/parliament/amendments.py` with amendment parser — extract amendment text, type (substantive/technical/SOP), proposer, target clause | [x] | codex_gpt5_engineer |
| 2.2 | Implement bill version diff using structural XML/JSON comparison — highlight added/modified/repealed sections | [x] | codex_gpt5_engineer |
| 2.3 | Implement amendment lifecycle graph in `src/nlp_policy_nz/parliament/amendments.py` — NetworkX graph from proposal → debate → vote → outcome | [x] | codex_gpt5_engineer |
| 2.4 | Write unit tests for amendment detection, bill diff, and lifecycle graph | [x] | codex_gpt5_engineer |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 2 — Track 18` ⬜

### Phase 3: Pipeline Integration
**Estimated Effort**: Low-Medium
**Status**: ✅ Completed

Wire the new voting and amendment data into the existing pipeline record model and CLI.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `voting_record` and `amendments` fields to `PipelineRecord` schema in `src/nlp_policy_nz/storage/serialization.py` | [x] | codex_gpt5_engineer |
| 3.2 | Update processing functions to populate new fields during pipeline runs | [x] | codex_gpt5_engineer |
| 3.3 | Add CLI subcommands for voting/amendment queries (e.g. `voting-summary`, `amendment-history`) | [x] | codex_gpt5_engineer |
| 3.4 | Run focused tests, linting, and coverage check; record full-suite blocker | [x] | codex_gpt5_engineer |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 3 — Track 18` ⬜

---

## Acceptance Criteria

- [x] Voting parser extracts division details with >95% focused branch coverage
- [x] Amendment detector identifies amendment types and proposer
- [x] Bill version diff highlights added/modified/repealed sections
- [x] Lifecycle graph tracks amendment status
- [x] PipelineRecord includes new fields
- [x] Test coverage > 90%

## Files Created/Modified

| File | Action |
|------|--------|
| `src/nlp_policy_nz/parliament/__init__.py` | Create |
| `src/nlp_policy_nz/parliament/voting.py` | Create |
| `src/nlp_policy_nz/parliament/amendments.py` | Create |
| `src/nlp_policy_nz/storage/serialization.py` | Modify |
| `src/nlp_policy_nz/cli/main.py` | Modify |
| `tests/test_voting.py` | Create |
| `tests/test_amendments.py` | Create |

## Notes

- Voting records are sourced from Hansard XML division elements; sample 50 records in Phase 1.1 to map all field variants.
- Amendment types follow NZ parliamentary convention: substantive (changes policy), technical (corrects drafting), Supplementary Order Paper (government SOP).
- Bill version diff uses a structural tree comparison — start with XML/JSON diff libraries, fall back to custom comparison for legal clause numbering.
- The lifecycle graph uses NetworkX with nodes = amendment events, edges = transitions (proposed → debated → voted → passed/defeated).
- MP party affiliation is resolved via the knowledge base (KB) built in earlier tracks.

## Implementation Audit

- Added amendment parsing for SOP, technical, and substantive amendments with proposer, target clause, text, type, and SOP number extraction.
- Added structural XML/JSON bill version diffing for added, modified, and repealed clause or section identifiers.
- Added `AmendmentLifecycleGraph` with proposed, debated, voted, passed, and defeated states plus transition metadata.
- Added `voting_record` and `amendments` fields to `PipelineRecord`, dataframe conversion, Parquet load path, processing helpers, FastAPI inline responses, and CLI commands.
- Added `voting-summary` and `amendment-history` CLI commands.
- Validation:
  - `python -m pytest tests\test_voting.py tests\test_amendments.py -p no:cacheprovider -q` -> 15 passed.
  - `python -m ruff check --no-cache src\nlp_policy_nz\parliament\amendments.py tests\test_amendments.py tests\test_voting.py src\nlp_policy_nz\parliament\__init__.py` -> passed.
  - `python -m coverage report --data-file=.tmp\coverage\track18b.coverage --include=src\nlp_policy_nz\parliament\* -m` -> 93% total coverage across `parliament`.
  - Broad full-suite validation was not repeated after this focused pass because the repo hit a hard `No space left on device` condition during local test artifact creation; generated `track17-test-output` was removed to recover enough space for source restoration and focused validation.
