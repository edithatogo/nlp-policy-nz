# Track 18: Voting Record Analysis & Legislative Amendment Tracking

**Dependencies**: Track 4, Track 7
**Parallelization Node**: Parliamentary Analytics
**Status**: Pending

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
**Status**: ⬜ Pending

Parse amendment text from debates and committee reports, detect changes between bill versions, and model the amendment lifecycle.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 2.1 | Create `src/nlp_policy_nz/parliament/amendments.py` with amendment parser — extract amendment text, type (substantive/technical/SOP), proposer, target clause | [ ] | |
| 2.2 | Implement bill version diff using structural XML/JSON comparison — highlight added/modified/repealed sections | [ ] | |
| 2.3 | Implement amendment lifecycle graph in `src/nlp_policy_nz/parliament/amendments.py` — NetworkX graph from proposal → debate → vote → outcome | [ ] | |
| 2.4 | Write unit tests for amendment detection, bill diff, and lifecycle graph | [ ] | |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 2 — Track 18` ⬜

### Phase 3: Pipeline Integration
**Estimated Effort**: Low-Medium
**Status**: ⬜ Pending

Wire the new voting and amendment data into the existing pipeline record model and CLI.

| # | Task | Status | Commit |
|---|------|--------|--------|
| 3.1 | Add `voting_record` and `amendments` fields to `PipelineRecord` schema in `src/nlp_policy_nz/storage/serialization.py` | [ ] | |
| 3.2 | Update processing functions to populate new fields during pipeline runs | [ ] | |
| 3.3 | Add CLI subcommands for voting/amendment queries (e.g. `voting-summary`, `amendment-history`) | [ ] | |
| 3.4 | Run full test suite, linting, and coverage check | [ ] | |

**Checkpoint**: `conductor(checkpoint): Checkpoint end of Phase 3 — Track 18` ⬜

---

## Acceptance Criteria

- [ ] Voting parser extracts division details with >95% accuracy
- [ ] Amendment detector identifies amendment types and proposer
- [ ] Bill version diff highlights added/modified/repealed sections
- [ ] Lifecycle graph tracks amendment status
- [ ] PipelineRecord includes new fields
- [ ] Test coverage > 90%

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