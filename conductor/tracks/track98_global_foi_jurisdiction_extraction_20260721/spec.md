# Track 98: Global FOI jurisdiction extraction

Issue: [nlp-policy-nz #144](https://github.com/edithatogo/nlp-policy-nz/issues/144). Programme: [foi-o #81](https://github.com/edithatogo/foi-o/issues/81).

Incrementally adapt the library to extract candidate process/rule information from each jurisdiction's pinned legislation, Gazette/equivalent and archived FOI cases. Extraction must bind source and effective/capture dates, jurisdiction/profile, ontology and model versions, confidence, spans and review status. Cross-jurisdiction mappings require explicit crosswalks.

Model output is candidate evidence only. It cannot certify legal outcomes, promote profiles or replace independent annotation/adjudication.

## Acceptance

- Each target has a versioned concept/rule adapter or an evidenced unsupported-language/source blocker.
- Positive and negative examples, schema checks, held-out evaluation and independent-oracle boundaries accompany each increment.
- Downstream case/process models receive only provenance-bearing reviewed candidates.
