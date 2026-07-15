# Hugging Face archive publication runbook

This runbook is the external handoff for Track 90 / issue #96. The repository
implements and tests the rights-safe materialization contract; a maintainer
must supply a real `ArchiveBundle` and an authenticated Hugging Face workflow
run before the public endpoint gate can pass.

## Preconditions

- The source bundle has been reviewed for rights and validates as
  `ArchiveBundle`.
- `HF_ARCHIVE_DATASET_ID` and `HF_ARCHIVE_COLLECTION_ID` are configured as
  repository/environment variables.
- `HF_TOKEN` is stored as the `hf-archive-publish` environment secret; it must
  have write access only to the intended dataset repositories.
- The release has a pinned commit, source checksum, schema version, source DOI
  references, and a Zenodo handoff record.

## Staged dry run

```bash
uv run --extra dev python scripts/plan_hf_archive.py \
  --bundle artifacts/archive-bundle.json \
  --output-dir .tmp/hf-archive \
  --dataset-id "$HF_ARCHIVE_DATASET_ID" \
  --collection-id "$HF_ARCHIVE_COLLECTION_ID"
```

Inspect `release-manifest.json`, `README.md`, `checksums.json`,
`completeness-report.json`, `provenance-attestation.json`, `sbom.json`, and
`zenodo-handoff.json`. The local verification must pass before publication.

## Authenticated publication

Run the `Publish structured HathiTrust archive` GitHub Actions workflow with
`publish=true`. The workflow materializes the same plan, uploads the staged
folder, and probes every declared configuration through the Dataset Viewer.
The run is not complete unless the uploaded commit, release manifest checksum,
and endpoint report are retained as artifacts.

## Endpoint gate

For each public dataset repository, verify metadata, configuration discovery,
and a first-row response:

```bash
curl -fsS "https://huggingface.co/api/datasets/$DATASET_ID"
curl -fsS "https://datasets-server.huggingface.co/splits?dataset=$DATASET_ID"
curl -fsS "https://datasets-server.huggingface.co/first-rows?dataset=$DATASET_ID&config=inventory&split=train"
```

HTTP 503 or missing configuration shards is a failed external gate. Do not
interpret a successful Hub metadata response as proof that the Dataset Viewer
can stream the data.
