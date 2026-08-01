🎯 **What:**
The file `src/nlp_policy_nz/linked_data/rdf.py` was completely missing its test coverage file. The shared RDF serialization and querying helpers (`bind_common_namespaces`, `rdf_sidecar_path`, `write_graph`, `query_graph`) were not validated by the pipeline test suite.

📊 **Coverage:**
- Test `bind_common_namespaces` ensures graph namespaces are mapped to `FOAF`, `SIOC`, and `SCHEMA` URIRefs successfully.
- Test `rdf_sidecar_path` evaluates that input filenames in `str` and `Path` formats generate deterministic `.ttl` outputs.
- Test `write_graph` sets up temporary workspaces to write an RDFLib `Graph` instance, asserting existence on the filesystem and specific semantic string inclusion in serialized data.
- Test `query_graph` runs local in-memory sparql tests on small sample datasets output to a temporary `.ttl` store asserting proper tabular variable extraction logic for query sets.

✨ **Result:**
Improved test coverage on the linked data logic, reducing technical debt and enabling safer refactoring in downstream dependencies that integrate with graph datasets over the Parquet outputs.
