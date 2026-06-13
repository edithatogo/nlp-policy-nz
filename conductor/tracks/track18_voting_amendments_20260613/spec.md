# Track 18: Voting Record Analysis & Legislative Amendment Tracking

**Dependencies**: Track 4 (Ingestion Engine), Track 7 (Downstream API)
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

## Ontologies & Standards

- **UK Parliament API Voting Ontology**: Patterns for voting records
- **OASIS LegalDocML AKN**: Amendment representation patterns

## Acceptance Criteria

- [ ] Voting parser extracts division details with >95% accuracy
- [ ] Amendment detector identifies amendment types and proposer
- [ ] Bill version diff highlights added/modified/repealed sections
- [ ] Lifecycle graph tracks amendment status
- [ ] PipelineRecord includes new fields
- [ ] Test coverage > 90%