---
title: Five-minute quickstart
description: Process a small text file and inspect extracted pipeline output.
---

# Five-minute quickstart

1. Create a small input file:

```bash
mkdir -p .tmp/examples
echo "The Minister must report by 1 July 2026." > .tmp/examples/act.txt
```

2. Process it:

```bash
pixi run nlp-policy-nz process \
  --input .tmp/examples/act.txt \
  --output .tmp/examples/act.parquet \
  --source legislation \
  --no-embeddings
```

3. Export a broad extraction manifest from an existing Parquet output:

```bash
pixi run nlp-policy-nz export-extractions \
  --parquet .tmp/examples/act.parquet \
  --output .tmp/examples/extractions.json \
  --retrieved-at 2026-06-30T00:00:00Z
```

Expected result: a source-grounded output file that can be fed into downstream
analysis, publication, or rules-as-code bridge workflows.
