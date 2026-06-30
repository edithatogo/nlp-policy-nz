---
title: System overview
description: C4 level 2 architecture for NLP Policy NZ.
---

# System overview

```mermaid
flowchart LR
  user["Researcher or downstream system"] --> cli["CLI / API"]
  cli --> ingestion["Ingestion and normalization"]
  ingestion --> extraction["Extraction framework"]
  extraction --> ontology["Ontology and rules-as-code bridge"]
  extraction --> storage["Parquet, LanceDB, RDF, JSON-LD"]
  storage --> publishing["HF, Zenodo, OSF, docs"]
  ontology --> publishing
```

Major subsystems:

- CLI and FastAPI entry points.
- Source-grounded ingestion for legislation and Hansard.
- Broad extraction framework for legal, temporal, entity, amendment, and
  rules-as-code outputs.
- Ontology mapping and linked-data export.
- Storage and publication adapters.
- Observability, benchmarking, and CI gates.
