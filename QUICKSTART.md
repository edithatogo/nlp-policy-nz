# Quickstart

1. Copy `.env.example` to `.env` and adjust any local paths you need.
2. Start the local stack:

```bash
docker compose up --build api lancedb model-cache qdrant
```

3. In a second shell, install the SDK extras:

```bash
pip install -e .[client]
```

4. Check the API:

```bash
python examples/client_health.py
```

5. Run a search:

```bash
python examples/client_search.py "climate change"
```

6. Try the inline processing example:

```bash
python examples/client_process.py "Kia ora, this is a test."
```

If you have the API exposed on a different host or port, set `NLP_POLICY_NZ_API_URL` before running the examples.
