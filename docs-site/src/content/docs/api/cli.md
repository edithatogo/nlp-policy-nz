---
title: CLI reference
description: Command-line reference generated from argparse help.
---

# CLI reference

```text
usage: nlp-policy-nz [-h] [--verbose]
                     {process,search,upload-dataset,deploy-space,archive-to-zenodo,release,provenance,export-rdf,sparql,knowledge-graph,voting-summary,amendment-history,rac-export,export-extractions} ...

NLP preprocessing pipeline for NZ legislation and Hansard corpora.

positional arguments:
  {process,search,upload-dataset,deploy-space,archive-to-zenodo,release,provenance,export-rdf,sparql,knowledge-graph,voting-summary,amendment-history,rac-export,export-extractions}
                        Available sub-commands.
    process             Process documents through the NLP pipeline.
    search              Search the vector index for similar documents.
    upload-dataset      Upload a Parquet dataset to the Hugging Face Hub.
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
    export-extractions  Export pipeline Parquet records as a broad extraction
                        manifest.

options:
  -h, --help            show this help message and exit
  --verbose, -v         Enable verbose (DEBUG) logging.
```
