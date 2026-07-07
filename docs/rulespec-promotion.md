# RuleSpec Promotion Contract

Track 78 defines the repository-side promotion boundary for reviewed
rules-as-code candidates. The contract is intentionally fail-closed and keeps
executable semantics downstream.

## Repo-Side Responsibilities

- Validate source proof: citation path, source SHA256, and source spans.
- Validate review state: candidate, reviewed, rejected, deferred, blocked, and
  promoted.
- Preserve reviewer evidence and oracle fixture references.
- Emit deterministic JSON and YAML handoff artifacts.
- Keep the RuleSpec runtime, executable formulas, and engine-specific logic out
  of this repository.

## Downstream Responsibilities

- Own the executable RuleSpec module layout.
- Implement reviewed formulas and runtime evaluation.
- Consume promoted handoff artifacts from this repository.
- Carry engine-specific PolicyEngine or OpenFisca logic after promotion.

## Artifact Boundary

This repository owns the reviewed handoff payload and its validators:

- `nlp_policy_nz.rulespec_promotion.RuleSpecPromotionHandoff`
- `nlp_policy_nz.rulespec_promotion.RuleSpecFormula`
- `nlp_policy_nz.rulespec_promotion.RuleSpecOracleFixtureRef`
- `nlp_policy_nz.rulespec_promotion.RuleSpecReviewerEvidence`

Downstream `rulespec-nz` owns the executable code generated from that handoff.

