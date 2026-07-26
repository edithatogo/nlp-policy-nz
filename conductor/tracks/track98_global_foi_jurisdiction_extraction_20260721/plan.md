# Plan

- [x] Foundation NZ legislation, Gazette and case intake baseline: candidate
  source manifest, pinned source digests, profile-isolated routing, and
  per-jurisdiction source-family validation.
- [~] Australian pilot, contrast and remaining-jurisdiction adapters.
  - [x] Replace production AU-CTH placeholder fixtures with a metadata-only,
    ontology-pinned authentic extraction bundle. Synthetic records now exist
    only under `tests/fixtures`; no source text or labels are committed.
    (`d94d720`; bundle SHA-256
    `66ce14dd8abcdec4b648137faf1536c5e40ad87969450913913ab93bbdd10129`)
  - [ ] Build the AU-NSW extraction bundle only after a non-empty,
    rights-cleared request artifact is approved and frozen. Legislation
    adapter evidence cannot substitute for an empirical request population.
- [ ] UK and European English adapters.
- [ ] Official Alaveteli deployment adapters, including language/reviewer-capacity gates.
- [ ] Germany, Spain and Ireland adapters.
- [ ] Canada federal, US federal and South Africa adapters.
- [ ] At every increment run positive/negative, held-out, provenance and cross-profile-isolation checks; stop at legal/profile and publication gates.

Current boundary: AU-CTH has a bounded, upstream-approved, ontology-pinned
metadata handoff. It does not include source text or labels and does not confer
gold, publication, redistribution, training, release, legal-certification, or
population-inference status. AU-NSW remains blocked on an approved authentic
request artifact; no placeholder may satisfy that gate.
