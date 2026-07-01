# Track 34 Evidence: Standards-Based Publication Protocol

## Implemented

- Added `docs/publication_protocol.md` with standards, methods, data,
  analysis, artifact inventory, reproducibility, limitations, and overclaim
  review sections.
- Added `data/publication/track34_protocol_evidence_map.json` to map
  publication claims to repository evidence, planned work, or blocker status.
- Added `tests/test_track34_publication_protocol.py` to enforce claim evidence,
  artifact inventory, and overclaim guardrails.
- Added `tests/test_track34_conductor.py` to enforce Conductor archive state and
  evidence naming.

## Boundary

- Track 32 and Track 33 outputs are described as fixture-bounded unless full
  corpus, graph, and vector inputs are supplied.
- Rules-as-code bridge artifacts are described as non-executable downstream
  metadata, not executable policy programs.
- Tracks 35-37 remain planned for figure production, public exploration, and
  manuscript automation.

## Validation

- Focused Track 34 tests passed locally.
- Ruff passed for the new Track 34 tests.
- JSON validation passed for `data/publication/track34_protocol_evidence_map.json`
  and Track 34 metadata.
- `git diff --check` passed.
