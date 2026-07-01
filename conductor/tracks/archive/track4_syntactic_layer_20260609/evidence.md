# Track 4 Evidence - Syntactic Parsing and Citation Extractor

Track 4 is complete for repo-side syntactic parsing and citation extraction scaffolding.

Implemented surfaces:

- `src/nlp_policy_nz/syntactic/pipeline.py` provides `create_nlp_pipeline()` and pipeline component constants, with Māori Guard integration.
- `src/nlp_policy_nz/syntactic/citations.py` provides NZ Act and provision-reference EntityRuler patterns plus `create_citation_ruler()`.
- `src/nlp_policy_nz/syntactic/chunking.py` provides sentence chunking and structured legislation/Hansard identifier helpers.
- `src/nlp_policy_nz/syntactic/__init__.py` exposes the stable syntactic API.

Validation evidence:

- `tests/test_syntactic.py` covers spaCy pipeline creation, Māori Guard presence, citation ruler placement, NZ Act examples, section/part/schedule references, and pattern structure.
- The Track 4 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Expanded citation coverage for every New Zealand legislative drafting variant remains future corpus-driven work.
- Parser quality against full-corpus gold annotations remains outside this initial repo-side track.
