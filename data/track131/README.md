# Track 131 OCR benchmark scaffold

This directory contains the repo-side, metadata-only slice for issue #131.
`benchmark_manifest.json` binds the existing Track 87 registry and stratified
fixture metadata to a no-cost-only run contract. It does not contain historical
page images, OCR outputs, weights, credentials, or paid-compute configuration.

Build the deterministic report shell with:

```text
python scripts/build_ocr_benchmark_scaffold.py
```

The report is intentionally `not_run`. Existing engines remain
`adapter_contract_only` because their engine version, model, container, SBOM,
and licence identities are not pinned. A measured comparison and any promotion
decision require rights-cleared page inputs and an independently provisioned
no-cost worker; this repository does not claim either gate is complete.

Validate a supplied rights-cleared intake bundle with:

```text
python scripts/validate_track131_intake.py --manifest <bundle>/intake.json --root <bundle> --report <bundle>/report.json
```

The validator is fail-closed and checks page-image and annotation hashes,
rights evidence, pinned engine/model/container/SBOM/licence metadata, and the
no-cost runner declaration. No historical source content or credentials are
checked into this repository.
