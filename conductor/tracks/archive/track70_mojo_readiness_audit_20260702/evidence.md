# Track 70 Evidence

## Official Source Review

- [System requirements](https://docs.modular.com/mojo/requirements/) state Mojo runs on Mac, Linux, and Windows via WSL, with Ubuntu 22.04 LTS or later as the continuously tested Linux target.
- [Install guide](https://docs.modular.com/mojo/manual/install) shows supported installation paths through `pixi` and `uv`, and recommends `pixi` for project setup.
- [Mojo FAQ](https://docs.modular.com/mojo/faq) confirms the SDK ships as `mojo` and `mojo-compiler`, and points licensing to Modular's Terms of Use.
- [Mojo roadmap](https://docs.modular.com/mojo/roadmap/) is explicitly directional, not a binding engineering plan.

## Audit Findings

- Mojo is suitable only as an optional Linux-first sandbox path in this repo.
- Native Windows is not a target; Windows workflows should keep the Python fallback.
- `pixi` is the most natural CI installation path because the repo already uses Pixi, while `uv` remains a valid local alternative.
- `mojo-compiler` is the right packaging shape for any later runtime-only use where the LSP and debugger are unnecessary.
- Licensing and redistribution should be treated as governed by Modular's Terms of Use until a more permissive open-source position exists.

## Candidate Shortlist

1. Deterministic string-heavy normalization and source hashing.
2. Small rule-filter or scoring kernels where parity is easy to prove.
3. Anything already well-served by Polars, LanceDB, or Rust/PyO3 should stay there.

## Decision

Proceed with Track 71 as a Linux-only optional sandbox. Defer any production Mojo dependency until Track 72 produces benchmark evidence that is materially better than the current Python and Rust-backed options.
