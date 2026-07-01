# Ontology Mapping Knowledge Graph

Track 29 records explicit ontology mappings as a source-grounded knowledge graph.
It doesn't infer mappings; inferred mappings belong in Track 30.

## Artifacts

- `data/ontologies/ontology_mappings.json`: canonical mapping manifest.
- `data/ontologies/ontology_mappings.schema.json`: JSON Schema for the manifest.
- `data/ontologies/ontology_mappings.ttl`: RDF/Turtle export.
- `data/ontologies/ontology_mappings.jsonld`: JSON-LD export.
- `data/ontologies/ontology_mapping_summary.json`: counts by predicate, review
  status, and standard.
- `data/ontologies/ontology_mapping_graph.mmd`: Mermaid standards-level graph.

## Mapping Records

Each mapping records:

- source and target standard;
- source and target class/property/concept;
- mapping predicate;
- confidence;
- method;
- provenance; and
- review status.

Supported predicates include `skos:exactMatch`, `skos:closeMatch`,
`skos:broadMatch`, `skos:narrowMatch`, `skos:relatedMatch`,
`owl:equivalentClass`, `owl:equivalentProperty`, `rdfs:subClassOf`,
`rdfs:subPropertyOf`, and `source:crosswalk`.

## Seed Crosswalks

The initial mapping graph includes explicit reviewed mappings for:

- LKIF normative effects to AKN and ODRL targets;
- FOAF `Person` to schema.org `Person`;
- SIOC discourse posts to AKN debate speech;
- PROV-O entities to DCAT datasets;
- DCAT to data.govt.nz and NZGLS dataset/resource metadata;
- AGLS to NZGLS resource metadata;
- extraction families to rules-as-code, OWL-Time, and SKOS targets.

Mappings with `needs_review` status are retained for inspection but excluded
from equivalent-concept resolution helpers.

## Query Helpers

Use `nlp_policy_nz.ontology.mapping_graph` for programmatic inspection:

```python
from nlp_policy_nz.ontology.mapping_graph import (
    get_equivalent,
    mappings_by_standard_pair,
    traverse_mappings,
)

people = get_equivalent("Person", "FOAF", "schema.org")
dcat_nzgls = mappings_by_standard_pair("DCAT", "NZGLS")
paths = traverse_mappings("Permission", "LKIF", max_hops=2)
```

## Known Gaps

- The graph is explicit only; it doesn't claim inferred class equivalence.
- Some mappings are close matches rather than semantic parity.
- Rules-as-code and extraction-family mappings require downstream review before code
  generation.
- SHACL validation shapes remain later-track work. Track 30 now provides
  review-only mapping inference candidates; explicit mappings in this document
  remain authoritative only after review.
