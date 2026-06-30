---
title: Decision records
description: Key architecture decisions and where to extend them.
---

# Decision records

Current decisions:

- Use Astro/Starlight for the documentation portal because it is already the
  declared project docs stack.
- Keep rules-as-code extraction as one output family inside a broader extraction
  framework.
- Store explicit ontology mappings separately from inferred mappings.
- Keep performance regression baselines in git and update them on master.

Future ADRs should record API authentication, production deployment, SDK shape,
and hosted documentation versioning choices.
