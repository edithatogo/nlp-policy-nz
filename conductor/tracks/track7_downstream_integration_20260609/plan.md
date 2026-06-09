# Plan: Track 7 Downstream API & Multi-Agent Verification

This track finalizes the public API surface for downstream consumers and implements cross-domain relational graphs.

---

### [x] Task 7.1: Expose Public Module APIs
- **Action**: Finalize public function exports for `corpus-law-nz` and `corpus-nz-hansard`.
- **Why**: Enables clean imports from downstream repos.
- **Completed**: Created `api.py` with `process_legislation()`, `process_hansard()`, and `search_similar()` high-level orchestration functions. Created `cli/main.py` with `process` and `search` subcommands via argparse. All sub-packages expose clean `__all__` exports.

### [x] Task 7.2: Code Relational Graphs
- **Action**: Implement NetworkX mapping layer linking debate mentions to legislation acts.
- **Why**: Enables cross-referencing between Hansard and Legislation corpora.
- **Completed**: Created `cli/graph.py` with `PolicyGraph` class wrapping NetworkX DiGraph, supporting `add_act()`, `add_speech()`, `add_citation()`, `add_section_reference()` and query methods (`query_acts_mentioned_in_speech()`, `query_speeches_mentioning_act()`, `query_most_cited_acts()`, `query_most_active_speakers()`), plus JSON serialization.

---
