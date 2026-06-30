---
title: Client SDK guide
description: Use the API from Python clients and future SDK wrappers.
---

# Client SDK guide

The formal client SDK is tracked separately. Until it lands, use the FastAPI
OpenAPI document to generate clients or call the service with standard HTTP
tools.

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/search",
    json={"query": "ministerial reporting duty", "top_k": 5},
    timeout=30,
)
response.raise_for_status()
print(response.json())
```

Once the SDK is available, this page should become the stable entry point for
authentication, retries, pagination, and typed response models.
