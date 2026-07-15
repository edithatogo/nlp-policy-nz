# FOI-O Archive Extraction Adapter

## Objective

Provide a deterministic, ontology-pinned adapter that converts bounded
`fyi-archive` inputs into reviewable FOI-O candidates without transferring
ontology ownership or promoting legal labels automatically.

## Must

- Preserve source spans, raw labels, uncertainty, disagreements, and complete
  source/model/ontology provenance.
- Keep every derived assertion candidate-only until real immutable inputs and
  independent empirical review support promotion.
- Fail closed for unknown labels, mismatched revisions, or invalid digests.
- Emit deterministic bundles and baseline deltas accepted by the archive
  handoff contract.

## Acceptance

- Focused contract, extraction, evaluation, and serialization tests pass.
- A promotion review records either an evidence-backed promotion or an explicit
  no-promotion decision.
- Missing empirical evidence is transferred to a separately tracked follow-up.
