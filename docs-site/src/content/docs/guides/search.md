---
title: Search guide
description: Semantic search, vector queries, and result filtering.
---

# Search guide

Semantic search uses embeddings and vector indexes over processed records.

```bash
pixi run nlp-policy-nz search \
  --query "climate change adaptation duties" \
  --top-k 5 \
  --db ./lancedb_data
```

Use filters at the dataset or application layer for jurisdiction, source type,
date, Act title, provision path, or debate metadata. Keep vector indexes
rebuildable from committed manifests and published dataset artifacts.
