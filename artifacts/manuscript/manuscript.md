# nlp-policy-nz: Evidence-bounded NLP infrastructure for New Zealand legal and policy corpora

## Abstract

We present `nlp-policy-nz`, a reproducible NLP pipeline for New Zealand legislation, Hansard, ontology mapping, graph/vector analysis, and publication packaging. The current submission is evidence-bounded: repo-side artifacts cover deterministic fixtures, checked-in ontology manifests, publication protocols, figures, tables, and an exploration Space, while full-corpus and live-publication claims remain explicit gates.

## Introduction

New Zealand legal and policy text combines legislation, parliamentary debate, Te Reo Maori concepts, public-sector metadata standards, and rules-as-code requirements. The project provides a shared core that makes those materials inspectable through structured extraction, ontology alignment, and release-oriented evidence bundles.

## Methods

The pipeline uses deterministic fixture inputs and checked-in manifests to document corpus statistics, ontology coverage, graph/vector outputs, and release protocols. Track 34 maps 14 publication claims to evidence states; Track 35 generates 12 tables, figures, and diagrams; Track 36 exposes those outputs through a Hugging Face Space.

## Results

The protocol currently records 9 repo-evidence claims, 3 blockers, and 1 external gates. The manuscript package includes generated tables, figure references, a supplement skeleton, arXiv requirements, and offline review-agent score records.

## Discussion

The central design decision is to separate reproducible repo evidence from claims that require full-corpus exports, credentials, or external service execution. This prevents overclaiming while preserving a clear path to publication once canonical data exports are supplied.

## Limitations

Full-corpus statistics, live Hugging Face or Zenodo publication evidence, and production-scale graph/vector analyses remain gated. The review loop is deterministic and offline; live external reviewer agents are intentionally not asserted as completed evidence.

## Conclusion

`nlp-policy-nz` provides an auditable scaffold for publication-grade legal NLP infrastructure. The next publication step is to replace fixture-bounded sections with canonical full-corpus outputs and rerun the same review loop against those artifacts.
