---
title: Five-minute quickstart
description: Process a small text file and inspect extracted pipeline output.
---

# Five-minute quickstart

1. Process the bundled legislation fixture:

```bash
pixi run nlp-policy-nz process \
  --input data/samples/sample_legislation.txt \
  --output .tmp/examples/legislation.parquet \
  --source legislation \
  --no-embeddings
```

2. Export a broad extraction manifest from the Parquet output:

```bash
pixi run nlp-policy-nz export-extractions \
  --parquet .tmp/examples/legislation.parquet \
  --output .tmp/examples/extractions.json \
  --retrieved-at 2026-06-30T00:00:00Z
```

Expected result: a source-grounded output file that can be fed into downstream
analysis, publication, or rules-as-code bridge workflows.

## Optional API path

The Docker Compose stack is an optional development/API workflow after the
fixture path. Its `lancedb` and `model-cache` services are Alpine volume-holder
stubs, not standalone LanceDB or model-serving services.
