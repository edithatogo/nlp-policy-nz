---
title: CLI reference
description: Command-line reference generated from argparse help.
---

# CLI reference

```text
usage: nlp-policy-nz [-h] [--verbose]
                     {process,search,upload-dataset,auth,deploy-space,archive-to-zenodo,release,provenance,export-rdf,sparql,knowledge-graph,voting-summary,amendment-history,rac-export,policyengine-pilot,multi-engine-parity,export-extractions,export-rac-candidates,export-nz-ontologies,corpus-stats,graph-vector-analysis,publication-protocol,generate-analysis-artifacts,generate-manuscript-package,quality,completion} ...

NLP preprocessing pipeline for NZ legislation and Hansard corpora.

positional arguments:
  {process,search,upload-dataset,auth,deploy-space,archive-to-zenodo,release,provenance,export-rdf,sparql,knowledge-graph,voting-summary,amendment-history,rac-export,policyengine-pilot,multi-engine-parity,export-extractions,export-rac-candidates,export-nz-ontologies,corpus-stats,graph-vector-analysis,publication-protocol,generate-analysis-artifacts,generate-manuscript-package,quality,completion}
                        Available sub-commands.
    process             Process documents through the NLP pipeline.
    search              Search the vector index for similar documents.
    upload-dataset      Upload a Parquet dataset to the Hugging Face Hub.
    auth                Manage API keys for secured API access.
    deploy-space        Deploy the Gradio visualization Space to Hugging Face
                        Hub.
    archive-to-zenodo   Archive a Parquet file to the Zenodo Sandbox.
    release             Create a versioned release archive and publish to
                        Zenodo.
    provenance          Display PROV-O provenance for a Parquet output.
    export-rdf          Export Hansard Parquet records as SIOC/FOAF Turtle
                        RDF.
    sparql              Run a SPARQL SELECT query over a Turtle RDF file.
    knowledge-graph     Export Wikidata-annotated entities as JSON-LD.
    voting-summary      Parse a Hansard division text file into a voting
                        summary.
    amendment-history   Parse amendment records from a Hansard or committee
                        text file.
    rac-export          Export one source section as a rules-as-code bridge
                        JSON-LD record.
    policyengine-pilot  Build the Track 79 PolicyEngine pilot package from a
                        reviewed manifest.
    multi-engine-parity
                        Build the Track 80 OpenFisca and PolicyEngine parity
                        bundle.
    export-extractions  Export pipeline Parquet records as a broad extraction
                        manifest.
    export-rac-candidates
                        Export batch rules-as-code candidate manifests and
                        bridge records.
    export-nz-ontologies
                        Export Track 31 NZ ontology candidates and controlled
                        vocabularies.
    corpus-stats        Export Track 32 corpus descriptive statistics.
    graph-vector-analysis
                        Export Track 33 graph, vector, and network analysis.
    publication-protocol
                        Export Track 34 standards-based publication protocol.
    generate-analysis-artifacts
                        Generate Track 35 tables, figures, diagrams, and
                        blockers.
    generate-manuscript-package
                        Generate Track 37 manuscript and review-agent
                        artifacts.
    quality             Inspect data quality validation, reports, dashboards,
                        and alerts.
    completion          Generate shell completions and a man page.

options:
  -h, --help            show this help message and exit
  --verbose, -v         Enable verbose (DEBUG) logging.
```
