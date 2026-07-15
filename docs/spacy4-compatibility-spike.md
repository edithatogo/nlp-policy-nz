# spaCy 4 compatibility spike

Date: 2026-07-14  
Track: `spacy4_compatibility_spike_20260714`  
Issue: [#104](https://github.com/edithatogo/nlp-policy-nz/issues/104)

## Decision

Defer adoption. Production remains on the locked spaCy 3.8.14 line. The
spaCy 4.0.0.dev3 wheel is usable only as an isolated Python 3.12 experiment
with an explicit pre-release resolver setting and `numpy<2`; it is not a
production-ready compatibility target.

## Evidence

The probe is reproducible with:

```bash
PYTHONPATH=src .tmp/spacy4-compat/bin/python scripts/spacy4_compatibility_spike.py \
  --output .tmp/spacy3.json
PYTHONPATH=src .tmp/spacy4-compat/bin/python scripts/spacy4_compatibility_spike.py \
  --output .tmp/spacy4.json
```

Both spaCy 3.8.14 and spaCy 4.0.0.dev3 produced identical token boundaries
for the fixed Māori/legal fixture and stable, repeated SHA-256 values for
`DocBin` serialization. The blank pipeline emits no entities, so the entity
span comparison is explicitly `[]` in both lanes. Blank-pipeline packaging and
the fixed 100 × 100-document benchmark workload were also stable within each
runtime:

| Check | spaCy 3.8.14 | spaCy 4.0.0.dev3 |
|---|---|---|
| Python 3.12.13 wheel | Pass | Pass with `--prerelease=allow` |
| Tokenisation fixture | Pass | Pass |
| `DocBin` serialization | Stable | Stable |
| Blank pipeline packaging | Stable | Stable |
| Māori guard tests | No regression observed | No regression observed |
| Transformers / Torch / bitsandbytes | Not installed | Not installed |

The same spaCy 4 environment first failed to import with `numpy==2.5.1`:
`ValueError: numpy.dtype size changed`. Reinstalling `numpy==1.26.4` allowed
the probe to run. This is a native-wheel compatibility risk, not an adoption
recommendation.

The existing deontic modality adapter also fails on spaCy 4 dev3 with a
Pydantic v1 forward-reference error while resolving the registered component:
`ConfigError: field "nlp" not yet prepared`. The same adapter succeeds on the
spaCy 3.8.14 environment and returns the expected `obligation` annotation.

Python 3.13 and 3.14 were checked with binary-only resolution. spaCy 4.0.0.dev3
has no usable wheels for either runtime. A follow-up Python 3.14 source build
also failed in `blis==0.7.11` during Cythonization, so 3.14 remains a canary
and cannot enter the supported matrix. The repository's existing spaCy 3.8
lock likewise only records wheel-supported lanes.

## Scope limits

No production dependency, Pixi lock, model package, or Transformers runtime
was changed. The spike does not claim NER accuracy or model parity because no
spaCy model or Transformers stack was installed in the isolated environments.
Those require a future upstream-release track with pinned model artifacts and
the full extraction-contract matrix.
