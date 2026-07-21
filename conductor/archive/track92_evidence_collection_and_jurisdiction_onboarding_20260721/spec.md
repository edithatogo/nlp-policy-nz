# Specification: Evidence Collection and Jurisdiction Onboarding

## Overview

Create a traceable, rights-aware collection workflow that supplies the
external evidence needed to close issues #132 and #133 and provides the
contract foundation and source inventory needed to implement issues #143 and
#144. `nlp-policy-nz` remains the orchestration and candidate-output project;
source repositories remain authoritative for source acquisition and provenance.

## Functional Requirements

1. Define one provenance-bearing evidence manifest shared by historical
   evaluation, archive assurance, concept-pack exports, and jurisdiction
   adapters.
2. Collect rights-cleared, volume-isolated Parliament evidence using
   `corpus-nz-hansard` and `hathi-nz`, with identities, temporal authority,
   annotations, adjudication, signatures, and measured evaluation results.
3. Execute and archive the Track 133 mixed-access assurance report, including
   serializer, compatibility, performance, mutation, rights-basis, and
   independent-review evidence.
4. Define a jurisdiction-neutral, candidate-only concept-pack and feedback
   contract aligned to `foi-o` and independently tested through
   `rac-conformance`.
5. Inventory and incrementally adapt legislation, Gazette, guidance, and FOI
   case sources using the existing legislation, FOI, archive, and mapping
   repositories.
6. Preserve jurisdiction, profile, version, source, effective-date,
   uncertainty, conflict, access, and review metadata throughout.
7. Keep all outputs candidate-only until rights, legal, profile-owner, and
   independent conformance gates pass.

## Non-Functional Requirements

- No credentials, restricted source text, private identities, or fabricated
  metrics are committed to public repositories.
- Every material artifact has an immutable identifier and cryptographic hash.
- Missing evidence produces a deterministic no-promotion result.
- Collection work is reproducible from pinned repository commits and source
  manifests.

## Acceptance Criteria

- #132 has a validated held-out report or an evidence-backed no-promotion
  report with all missing inputs explicitly listed.
- #133 has an archived assurance run with independent review and rights basis.
- #143 has a versioned export and feedback contract with conformance fixtures.
- #144 has a source inventory and at least one jurisdiction adapter with
  positive, negative, temporal, and non-equivalence fixtures.
- Cross-repository provenance links are recorded in `nlp-policy-nz`.

## Out of Scope

- Making legal interpretations authoritative without human review.
- Publishing restricted images, annotations, identities, or credentials.
- Claiming empirical model completion from schemas or synthetic fixtures.
- Implementing every FOI-O jurisdiction in one change.
