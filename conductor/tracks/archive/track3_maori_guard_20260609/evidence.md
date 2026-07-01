# Track 3 Evidence - Māori Language Guard

Track 3 is complete for repo-side Māori language guard scaffolding.

Implemented surfaces:

- `src/nlp_policy_nz/guard/normalizer.py` provides NFC normalization, macron detection, macron preservation, and canonical mappings for common Māori forms.
- `src/nlp_policy_nz/guard/tokenizer_exceptions.py` provides Te Reo Māori lexical atom sets, tokenizer exception construction, and a spaCy guard component factory.
- `src/nlp_policy_nz/guard/language_id.py` provides optional lingua-rs backed phrase-level language detection for English, Te Reo Māori, and uncertain text.
- `src/nlp_policy_nz/guard/__init__.py` exposes the stable guard API while lazily loading optional language detection exports.

Validation evidence:

- `tests/test_guard.py` covers Unicode NFC normalization, macron handling, lexical atom coverage, spaCy tokenizer exceptions, component idempotency, English detection, Māori detection, low-confidence handling, and code-switch segmentation.
- The Track 3 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Broader linguistic validation with domain experts remains outside this repo-side track.
- Expanded dialectal and orthographic coverage should be handled as future corpus-driven improvements rather than claimed by this initial guard layer.
