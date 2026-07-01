# Track 7: Design Downstream API and Multi-Agent Verification

**Status**: Complete

## Goal

Expose stable downstream entrypoints for processing, search, and relational graph analysis so other repos and tools can consume `nlp-policy-nz` outputs without depending on internal module details.

## Scope

- Public process/search wrappers for legislation and Hansard workflows.
- CLI `process` and `search` subcommands.
- NetworkX-backed `PolicyGraph` for linking speeches, acts, sections, speakers, bills, and debates.
- JSON serialization for relational graph outputs.

## Acceptance Criteria

- API wrappers expose `process_legislation`, `process_hansard`, and `search_similar`.
- CLI parser accepts and validates process/search arguments.
- `PolicyGraph` can add act/speech nodes, citation edges, section-reference edges, and query ranked graph relationships.
- Graph serialization round-trips through JSON.
- Tests cover CLI parsing and graph behavior without requiring live services.

## Evidence Boundary

Track 7 is complete for repo-side downstream API and graph scaffolding. It does not claim production API hardening, authentication, or full multi-agent orchestration; those are later Conductor tracks.
