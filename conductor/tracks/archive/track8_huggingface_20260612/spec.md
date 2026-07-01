# Track 8: Deploy Hugging Face Datasets and Interactive Visualization Spaces

**Status**: Complete

## Goal

Publish pipeline Parquet outputs to Hugging Face dataset repositories and provide a Gradio Space for interactive exploration of the processed corpus.

## Scope

- Convert local Parquet pipeline outputs into `datasets.Dataset` objects.
- Create or update Hugging Face dataset repositories and push splits with commit metadata.
- Generate dataset cards with YAML frontmatter, schema details, pipeline notes, and citation text.
- Provide a Gradio Space with search, citation-network, Te Reo term-frequency, and corpus-statistics views.
- Support dry-run Space deployment for offline validation.

## Acceptance Criteria

- The Python API can convert Parquet data to a Hugging Face `Dataset`.
- Upload and Space deployment helpers use explicit tokens or `HF_TOKEN` and fail clearly when credentials or files are missing.
- CLI commands expose dataset upload and Space deployment workflows.
- Tests mock Hugging Face Hub calls so the default validation path is offline.
- The Space transformation logic is covered without requiring a live Gradio deployment.

## Evidence Boundary

Track 8 is complete for repo-side upload/deploy tooling and local interactive Space source. It does not claim that production datasets or Spaces have been published to a live Hugging Face namespace; automated publication and public exploration expansion belong to later release/site tracks.

