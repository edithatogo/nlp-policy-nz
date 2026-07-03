# Track 63: nlprule Grammar and Rule Matching Evaluation

Track 63 evaluates whether nlprule-style grammar and rule matching should be
introduced as an optional rule engine for legal drafting quality checks and
structured extraction cues.

## Requirements

- Preserve spaCy as the maintained and default tokenization and matching path.
- Evaluate nlprule-style grammar matching without adding a required dependency.
- Keep Te Reo Māori token preservation intact, including macronized forms.
- Map rule output into the repo's existing extraction and quality schemas.
- Record a clear decision on whether nlprule stays optional, experimental, or
  rejected as a required dependency.

## Acceptance Criteria

- [ ] Library viability is assessed before dependency changes.
- [ ] A prototype or documented rejection compares nlprule with spaCy rules.
- [ ] Māori token preservation and legal span alignment tests pass.
- [ ] Rule outputs are mapped to existing quality/extraction schemas.
- [ ] A decision record defines adoption scope or rejection rationale.

## Non-Goals

- Replacing spaCy pipeline components.
- Making nlprule a required runtime dependency.
- Changing the canonical extraction families or schema definitions.

