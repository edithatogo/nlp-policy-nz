# spaCy 4 compatibility spike

Evaluate spaCy 4 in an isolated, non-production environment against the
current stable spaCy 3.8 line used by the FOI extraction adapter.

The spike must also reconcile the repository's Python policy: production uses a
wheel-supported Python 3.12 lane; Python 3.13/3.14 are explicit canaries until
spaCy, PyTorch, bitsandbytes, and the other native dependencies are verified.
spaCy 4 is not a production target merely because a development wheel exists.

## Acceptance

- Compare tokenisation, entity spans, serialization, model packaging, Python
  3.12–3.14, and Transformers compatibility.
- Record deterministic benchmark, accuracy, and reproducibility evidence.
- Production remains on the latest stable supported line until the spike and
  upstream release status justify a migration.
- No spaCy 4 dependency change is allowed without a passing rollback-tested
  compatibility matrix and a recorded adoption decision.
