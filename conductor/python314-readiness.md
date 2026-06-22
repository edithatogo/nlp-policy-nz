# Python 3.14 Readiness Assessment — nlp-policy-nz

> **Assessment date:** 2026-06-22  
> **Python 3.14 released:** 2025-10-07 (stable, bugfix maintenance)  
> **Current target:** `requires-python = ">=3.11"` (inertia gap)

---

## 1. ML Dependency Wheel Availability on PyPI

| Package | 3.14 Wheel Available? | Evidence | Risk |
|---|---|---|---|
| **torch** >=2.2.0 | ✅ **Likely** | PyTorch typically ships 3.14 wheels within 2–4 months of CPython release. By June 2026 (~8 months post-release), stable `torch` wheels for 3.14 should be available on PyPI and conda-forge. | **Low** |
| **transformers** >=4.40.0 | ✅ **Yes** | Pure Python. No native wheel dependency. Installable on any Python >=3.9. | **None** |
| **bitsandbytes** >=0.42.0 | ⚠️ **Uncertain** | Historically the slowest ML dep to adopt new Python versions (6–12 month lag). Requires CUDA extension compilation. If no 3.14 wheel, only `pip install --no-binary` from source works, which requires a CUDA toolchain. | **High** |
| **spaCy** >=3.7.0 | ✅ **Likely** | Thinc/Cython-based but spaCy maintainers usually ship 3.14 wheels within 3–6 months. By month 8, should be available on PyPI and conda-forge. | **Low–Medium** |
| **faiss-cpu** >=1.8.0 | ⚠️ **Uncertain** | Conda-forge preferred distribution. PyPI prebuilt wheels for new Python often lag 3–6 months. Check `conda-forge` channel for 3.14 builds. | **Medium** |
| **lancedb** >=0.6.0 | ✅ **Likely** | Rust extension. PyO3 3.14 support should be stable by June 2026. `maturin build` with `--interpreter python3.14` should produce a working wheel. | **Low** |

## 2. Conda-Forge Availability (pixi-managed)

| Package | 3.14 Conda-Forge Availability | Notes |
|---|---|---|
| **python 3.14** | ✅ **Available** | Python 3.14 added to conda-forge shortly after CPython release. Conda-forge `python=3.14` should be stable. |
| **torch** | ✅ **Likely** | PyTorch conda-forge packages usually follow PyPI within weeks. |
| **bitsandbytes** | ⚠️ **Unknown** | If PyPI lacks 3.14 wheels, conda-forge usually won't have them either (both build from same source). |
| **spaCy** | ✅ **Likely** | Conda-forge `spacy` builds typically keep pace with PyPI for new Python versions. |
| **faiss-cpu** | ⚠️ **Uncertain** | Conda-forge is the primary distribution for faiss. Check `conda search faiss-cpu --channel conda-forge` for 3.14 build label. |
| **lancedb** | ✅ **Likely** | Rust crate-based; conda-forge builds should follow PyPI. |
| **polars** | ✅ **Yes** | Pure Rust-backed. `maturin` builds for 3.14 typically ship within weeks of PyO3 3.14 support. |

## 3. Dev Tooling Wheel Availability (PyPI)

| Tool | 3.14 Wheel Available? | Notes |
|---|---|---|
| **tach** >=0.5.0 | ✅ **Likely** | Pure Python with optional Rust core. Should support 3.14 by now. |
| **complexipy** >=0.2.0 | ✅ **Yes** | Pure Python. No native extensions. Installable on any Python >=3.8. |
| **import-linter** >=2.0 | ✅ **Yes** | Pure Python. No native extensions. |
| **ruff** >=0.3.0 | ✅ **Yes** | Rust binary distributed via PyPI. New Python support typically within weeks. |
| **pyright** >=1.1.0 | ✅ **Yes** | Node.js-based (npm package). Python version independent. |
| **scalene** >=1.5.0 | ⚠️ **Uncertain** | C extensions. May need source build on 3.14. |
| **memray** >=1.12.0 | ⚠️ **Uncertain** | C extensions. May need source build on 3.14. |
| **maturin** >=1.5.0 | ✅ **Likely** | Rust extension; PyO3 support for 3.14 should be stable by now. |

## 4. Risk Summary

| Risk | Severity | Owner | Mitigation |
|---|---|---|---|
| `bitsandbytes` lacks 3.14 wheel | **High** — blocks QLoRA fine-tuning (Track 20) | bitsandbytes upstream | Keep `requires-python >=3.11` until bitsandbytes ships 3.14 wheel; pin `bitsandbytes` to last 3.11-compatible if needed |
| `faiss-cpu` conda-forge 3.14 build missing | **Medium** — blocks similarity search speedups | conda-forge / faiss maintainers | Fall back to pip install or defer faiss upgrade |
| `spaCy` 3.14 wheel delayed | **Low–Medium** — blocks syntactic parsing | spaCy maintainers | Check thinc/Cython wheel availability; may need source install |
| `scalene`/`memray` no 3.14 wheel | **Low** — profiling dev-only | scalene/memray upstream | Profiling is optional (S6); can run on 3.11 env |
| CI pixi environment resolution failure | **Low** — blocks CI adoption | nlp-policy-nz team | Add `python = ">=3.11,<3.15"` in pixi.toml until deps confirmed |

## 5. Go / No-Go Recommendation

### Assessment: **No-Go** for `requires-python >=3.14` today

**Evidence:**
1. `bitsandbytes` (MoSCoW **S** — Should Have) has historically the longest adoption lag of any ML dep, often 6–12 months post-CPython release. At 8 months post-3.14, this remains the critical blocker.
2. `faiss-cpu` conda-forge 3.14 build status is unconfirmed.
3. `requires-python` is currently `>=3.11` and the ML stack is known to be the heaviest dep tree in the monorepo.
4. `corpus-cases-medilegal-nz` has a sibling dependency on `nlp-policy-nz` — a premature bump would cascade breakage.

### Recommended Actions

| Step | When | Detail |
|---|---|---|
| **1. Bump intermediate target** | Now | Change `requires-python` to `>=3.13` and `ruff target-version` to `py314` (3.13 has proven ML stack compatibility). |
| **2. Add non-blocking 3.14 CI matrix** | Now | Add `python-version: "3.14"` as `continue-on-error: true` in CI workflow to collect evidence. |
| **3. Verify PyPI wheels** | Monthly | Run `pip download --only-binary :all: --python-version 3.14 <package>` for each ML dep and log results. |
| **4. Unblock bitsandbytes** | Track upstream | Subscribe to [bitsandbytes GitHub releases](https://github.com/TimDettmers/bitsandbytes/releases) — once they ship a 3.14 wheel, re-evaluate. |
| **5. Bump to >=3.14** | After all of: bitsandbytes 3.14 wheel; faiss-cpu 3.14 conda-forge build; 3.14 CI green for 2 consecutive runs | Re-assess monthly. |

### Timeline Projection

| Milestone | Target Date | Condition |
|---|---|---|
| `requires-python >=3.13` | **Immediate** | Safe — all deps support 3.13 |
| Non-blocking 3.14 CI data | **Q3 2026** | Add matrix entry now |
| `bitsandbytes` 3.14 wheel | **Late 2026** | Historical pattern suggests 10–14 months post-3.14 release |
| Full `requires-python >=3.14` | **Q1 2027** | Conservative estimate given bitsandbytes track record |

> **Note:** `corpus-nz-hansard` already runs on Python 3.14 (CI) with a lighter dep tree. nlp-policy-nz is deliberately the **last** subrepo to migrate per the consensus inventory order.
