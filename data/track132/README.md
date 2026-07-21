# Track 132 Historical Parliament Held-Out Evaluation

This directory contains only the repo-side contract for issue #132. The manifest
is metadata-only: it contains no Parliament text, OCR payload, annotations,
speaker identities, or authority assertions.

The validator requires page-level uniqueness, volume/source/hash isolation across
splits, separate annotator and adjudicator roles, authority evidence references,
and signed review decisions. The report remains `no-promotion` until external
rights-safe annotations and measured evaluation metrics are supplied.

Run the executable intake check from the repository root:

```text
uv run --no-sync python scripts/validate_track132_intake.py
```

The empty checked-in intake is intentionally valid but cannot promote. Supply
rights-safe records and evidence by reference in `intake_manifest.json`, and
measured metrics in `evaluation_inputs.json`; do not commit Parliament text,
annotations, identity evidence, authority evidence, signatures, or fabricated
metrics to this repository.
