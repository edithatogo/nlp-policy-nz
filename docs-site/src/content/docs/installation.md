---
title: Installation
description: Install NLP Policy NZ with Pixi, pip, Docker, or future binaries.
---

# Installation

## Pixi development install

```bash
pixi install
pixi run test
```

Use Pixi for full development because it manages Python, Node, Rust, benchmark,
profiling, and documentation tooling consistently across platforms.

## Pip install

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

The core install keeps API, Space, and embedding stacks optional:

| Extra | Adds |
| --- | --- |
| `api` | FastAPI and Uvicorn |
| `space` | Gradio and Plotly |
| `ml` | Transformers, PyTorch, and bitsandbytes |
| `client` | HTTP client support |
| `orchestration` | Haystack governance orchestration |

Install only the integrations needed, for example `pip install "nlp-policy-nz[api,ml]"`.

On Linux or macOS, replace the activation path with the platform equivalent.

## Docker

Container packaging is tracked separately from this documentation site. Until
the production Docker image is finalized, use Pixi for repeatable local runs and
CI for hosted validation.

## Binary distribution

Binary builds are planned with the cross-platform distribution track. Treat any
local executable wrapper as experimental until release notes name a signed
artifact.
