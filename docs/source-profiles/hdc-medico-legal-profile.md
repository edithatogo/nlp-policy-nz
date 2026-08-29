# HDC medico-legal source profile

This design profile defines the active processing boundary for public New Zealand Health and Disability Commissioner decisions.

## Repository responsibilities

- `archive-govt-nz` owns public-source capture, fixity, version relations and replay receipts.
- `nlp-policy-nz` owns neutral extraction, evidence spans, missingness and source-linked record production.
- the existing Hugging Face dataset `edithatogo/corpus-cases-medilegal-nz` remains the canonical public normalised dataset identity.
- project-specific interpretation and coding belong in the consuming research repository, not in the canonical source record.

The archived GitHub corpus repository is historical provenance only and should not receive new implementation work.

## Record separation

The processing pipeline must preserve separate layers for:

1. captured source bytes and capture metadata;
2. extraction evidence and source spans;
3. official findings expressed in the authoritative decision;
4. neutral bibliographic and case metadata;
5. project-derived classifications, which remain downstream and reversible.

An extractor may propose a candidate finding span, recommendation span or review/remedy span. It may not infer a legal conclusion, clinical truth, credentialing failure or Decision Autopsy score.

## Evidence and uncertainty

Every candidate record should retain the authoritative URL, source content digest, retrieval receipt, record revision and extraction uncertainty. Missing or ambiguous fields remain missing or ambiguous. Extraction output must not silently overwrite a reviewed canonical record.

## Privacy and cultural limits

The profile should use minimum-necessary public metadata and avoid amplifying personal information beyond the authoritative public source without review. Correct Māori orthography and source-carried cultural terms should be preserved. Technical conformance does not constitute Māori, consumer, legal or clinical validation.

## Publication boundary

Publication to the existing Hugging Face dataset requires separate validation of row schema, rights, privacy, versioning and release status. This profile does not itself publish rows.

## Claim boundary

A passing profile and fixtures would establish a reproducible neutral-processing contract. They would not establish corpus completeness, legal interpretation, clinical truth, cultural authority, credentialing conclusions or downstream research validity.

Related issue: #313.
