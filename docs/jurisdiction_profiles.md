# Jurisdiction profile cookbook

Jurisdiction profiles are versioned routing contracts. Start by copying the
shape of `config/jurisdictions/nz.json`, choose an explicit `profile_id`, set
the country, corpus prefix, and existing candidate adapter, then recompute the
SHA-256 digest over the unsigned fields. Do not reuse a digest after editing a
profile.

Load a profile and route to its candidate-only adapter:

```python
from nlp_policy_nz.extraction.profile_router import load_profile_adapter

adapter = load_profile_adapter("nz")
```

Unknown profile IDs, malformed fields, and digest changes fail closed. A new
profile must first be tested against a licensed smoke fixture, then evaluated
against an appropriate oracle. Profile loading does not establish legal
equivalence, rights clearance, empirical quality, or promotion readiness.

The stable extraction surface is the profile router plus the existing adapter
modules under `nlp_policy_nz.extraction`. Adapter outputs remain candidate-only
and review-bound.
