# Track 54: Revisit Track 19 Profiling Gates After NZ Model Fine-Tuning

**Dependencies**: Track 19, Track 20
**Parallelization Node**: Observability Follow-Up
**Status**: New

## Overview

Track 19 has its repo-side implementation in place, but the remaining profiling
gates are still external:

- a 1 GiB Scalene profile on a supported runtime
- a 1 GiB Memray trace and flamegraph on a supported runtime
- any canonical full-corpus profiling pass when the corpus is available

This track exists so those gates can be revisited after NZ legal model
fine-tuning work lands and the profiling environment is available.

## Functional Requirements

1. Reassess the profiling gate plan after Track 20 produces a relevant NZ legal
   model checkpoint or benchmark milestone.
2. Confirm the profiling host can run Memray on the target platform.
3. Rerun Track 19 profiling wrappers against a corpus that satisfies the
   recorded minimum input size for the external gates.
4. Refresh Track 19 evidence and manifest entries with the new profiling
   outcome.
5. Decide whether Track 19 can be archived or whether a further follow-up is
   needed.

## Non-Functional Requirements

1. Preserve existing profiling evidence unless a new run produces a valid
   replacement artifact.
2. Keep the follow-up narrowly scoped to profiling gate closure.
3. Avoid claiming gate completion unless the recorded artifacts satisfy the
   minimum corpus and runtime requirements.

## Acceptance Criteria

1. A supported profiling environment has been verified for the target host.
2. New Scalene and Memray evidence artifacts exist for the required corpus
   size, or the track records a concrete blocker with provenance.
3. Track 19 evidence and any related manifest notes have been updated to match
   the new outcome.
4. The follow-up is either closed out with Track 19 archived or left open with
   a clearly documented blocker.

## Out of Scope

1. Training or tuning the NZ legal models themselves.
2. Reworking the profiling wrappers unless a gate failure proves they need it.
3. Changing the Track 19 benchmark semantics.
