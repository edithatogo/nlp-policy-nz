# Quickstart

The first-run path is local and does not require Docker, Qdrant, model
downloads, or embeddings.

1. Install the package:

```bash
pip install nlp-policy-nz
```

2. Process the bundled legislation fixture:

```bash
nlp-policy-nz process \
  --input data/samples/sample_legislation.txt \
  --output .tmp/examples/legislation.parquet \
  --source legislation \
  --no-embeddings
```

3. Optional API/Compose workflow: copy `.env.example` to `.env` and adjust
any local paths you need, then start the development stack:

```bash
docker compose up --build api lancedb model-cache qdrant
```

4. In a second shell, install the SDK extras:

```bash
pip install -e .[client]
```

5. Check the API:

```bash
python examples/client_health.py
```

6. Run a search:

```bash
python examples/client_search.py "climate change"
```

7. Try the inline processing example:

```bash
python examples/client_process.py "Kia ora, this is a test."
```

If you have the API exposed on a different host or port, set `NLP_POLICY_NZ_API_URL` before running the examples.
