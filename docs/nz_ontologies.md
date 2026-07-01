# New Zealand ontology candidates

Track 31 adds a deterministic, repo-side induction layer for New Zealand legal
and parliamentary ontology candidates. The implementation is intentionally
review-bounded: it uses current repository evidence from the ontology coverage
audit and mapping graph, and it doesn't claim full-corpus induction until the
whole-corpus statistics track produces dataset-wide counts.

## Application areas

The first bundle covers five application areas:

- Act structure ontology: Acts, Bills, provisions, amendments, commencement,
  and stable section anchors.
- Hansard debate topic ontology: debate speeches, questions, votes, and topic
  labels for parliamentary analysis.
- NZ court hierarchy ontology: court levels, judgments, and citation metadata.
- Māori legal concept ontology: reviewable terms from Māori legal sources that
  must preserve macrons and source evidence.
- NZ government agency ontology: departments, Crown entities, portfolios,
  offices, and public-sector organization classes.

## Evidence model

Each candidate concept records:

- a stable `https://legal-nz.example.org/ontology/nz/...` URI;
- an application area and concept kind;
- whether the concept is authoritative external vocabulary or induced NZ
  vocabulary;
- corpus or repository evidence, including Track 25 coverage rows and Track 29
  mapping records;
- ontology anchors to external standards such as AKN, ELI, ECLI, SIOC, SKOS,
  LKIF, actor vocabularies, and W3C ORG;
- confidence and review status.

Induced NZ concepts remain `needs_review`. Only externally authoritative
classes that are represented as local crosswalk concepts are marked `approved`.

## Exports

The generated artifacts are written under `data/ontologies/`:

- `nz_ontology_candidates.json`
- `nz_ontology_candidates.ttl`
- `nz_ontology_candidates.jsonld`
- `nz_controlled_vocabularies.json`

The RDF export includes concept classes, provenance links, confidence values,
review status, ontology anchors, and SKOS concept schemes. The SKOS export
contains controlled vocabularies for NZ Act types, Hansard topics, court
levels, government agencies, and Māori legal concepts.

## Boundary

This track satisfies the deterministic repo-side ontology layer. Full-corpus
frequency induction, temporal trend counts, live publication, and authenticated
external-source reconciliation remain future work until the required data and
access are available.
