# Python Runtime Matrix

The repository keeps dependency claims explicit because the scientific Python
stack does not publish compatible wheels for every Python release at the same
time.

| Lane | Python | Purpose | spaCy/PyTorch stack |
| --- | --- | --- | --- |
| Production | 3.12 | Default local, release, and deployment runtime | Required |
| Compatibility CI | 3.11 | Older supported compatibility lane | Required |
| Experimental | 3.13 | Early compatibility signal | Probe only; no production guarantee |
| Experimental | 3.14 | Resolver and application-runtime probe | Deliberately omitted |

Python 3.14 is not a production target. spaCy 3.8.x, PyTorch, and
bitsandbytes are gated to Python versions below 3.14 in both `pixi.toml` and
`pyproject.toml`. This prevents uv and Pixi from claiming that a 3.14 full NLP
environment is installable when the required wheels are unavailable.

## Environment Profiles

The default and `production` environments are Python 3.12 CPU environments:

```bash
pixi install
pixi install -e production
```

The GPU profile is opt-in and runs a CUDA availability check against the
installed PyTorch build. It requires a Linux host with a working NVIDIA driver:

```bash
pixi install -e gpu
pixi run -e gpu gpu-check
```

The profiling profile is intentionally pinned to Python 3.12 so profiling
results are comparable with production:

```bash
pixi install -e profiling
pixi run -e profiling profile
```

The experimental environments are limited to dependency-resolution and runtime
compatibility checks. They are not included in the full test matrix:

```bash
pixi install -e py313-experimental
pixi install -e py314-experimental
```

When spaCy 4 and the related ML wheels support Python 3.14, the markers and the
experimental lane can be reassessed together. No spaCy 4 migration is implied
by the current configuration.
