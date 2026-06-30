---
title: Publishing guide
description: Publish datasets and archives to Hugging Face, Zenodo, and OSF.
---

# Publishing guide

The CLI includes Hugging Face and Zenodo commands for dataset publication and
citable release archives.

```bash
pixi run nlp-policy-nz upload-dataset \
  --parquet output/legislation.parquet \
  --repo-id owner/nz-legislation
```

```bash
pixi run nlp-policy-nz release \
  --parquet output/legislation.parquet \
  --version 1.0.0 \
  --title "NZ legislation corpus v1.0" \
  --description "Versioned corpus release" \
  --creators '[{"name": "Maintainer"}]'
```

Publication records should include provenance sidecars, source hashes, schema
versions, and artifact checksums.
