# spaCy 4 Compatibility Spike

This is an isolated evaluation for issue #104. It does not change the
production runtime. Production remains on the locked spaCy 3.8.14 baseline;
the existing project manifests continue to gate spaCy below version 4.

## Scope

The repository does not expose a separately named FOI-O adapter. The closest
source-to-span adapter is `src/nlp_policy_nz/xml_parser.py`, which parses
structured NZ legislative XML, aligns character offsets to spaCy spans, and
feeds the portable extraction manifest serializer. The spike uses that path as
the compatibility fixture and records the scope limitation explicitly.

The harness covers:

- XML structure extraction and entity span alignment;
- deterministic extraction-manifest serialization and hashes;
- Python and spaCy/Transformers versions;
- isolated candidate installation and importability;
- benchmark timing and reproducibility metadata; and
- rollback policy and the absence of a labelled accuracy set.

Run the baseline evidence locally:

```bash
pixi run python scripts/spacy4_compatibility_spike.py
```

Attempt the newest PyPI spaCy 4 prerelease in a disposable uv environment:

```bash
uv run --no-project python scripts/spacy4_compatibility_spike.py --probe-candidate
```

The candidate probe must use `--prerelease=allow` and never modifies the
project lockfiles or production environment.

## Result

PyPI currently exposes `4.0.0.dev3` as the newest spaCy 4 prerelease, while
`3.8.14` is the current stable 3.x release. The Python 3.12 candidate probe
installs the prerelease but fails on import with a NumPy/Thinc binary ABI
mismatch. The result is therefore `candidate_blocked`; no production switch is
justified.

The committed machine-readable evidence is
`artifacts/track104/spacy4_compatibility_spike.json`. The fixture has no
labelled FOI-O gold set, so accuracy is recorded as `not_measured` rather than
inferred from span alignment. Re-run the spike when a labelled set and a
supported spaCy 4 release are available.
