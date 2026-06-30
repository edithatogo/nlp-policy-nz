---
title: Ingestion guide
description: Import legislation and Hansard corpora into pipeline records.
---

# Ingestion guide

The ingestion layer accepts legislation and Hansard text inputs, normalizes text,
chunks source documents, extracts citations and Te Reo Māori terms, and writes
structured records for storage and downstream use.

## Legislation

Use `process --source legislation` for Acts, Bills, and provision-level text.
Prefer source-grounded inputs that include authoritative URLs, retrieval dates,
and citation paths when they are available.

## Hansard

Use `process --source hansard` for debate text. Hansard processing can add
argument, stance, voting, amendment, FOAF, and SIOC-linked discourse outputs
when the relevant modules have enough structure to parse.

## Provenance

Keep source URLs, retrieval timestamps, and checksums with any corpus export.
Those fields support stale-source checks, publication manifests, and
rules-as-code traceability.
