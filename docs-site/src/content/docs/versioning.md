---
title: Versioned documentation
description: How latest and tagged documentation builds are published.
---

# Versioned documentation

The `latest` documentation build follows `master`. Tagged releases should keep a
matching documentation build so API, CLI, and runbook instructions remain
auditable against the code that produced them.

The docs workflow builds on pull requests and publishes on pushes to `master`.
When a git tag is cut, the same site content should be treated as the
documentation for that release tag. A future release workflow can copy the built
site under a tag-specific prefix if hosted version switching becomes required.

The site sidebar keeps this page visible so users can distinguish current
documentation from release-specific evidence.

<label for="docs-version">Documentation version</label>
<select id="docs-version" name="docs-version">
  <option selected>latest (master)</option>
  <option disabled>release tags publish from v*</option>
</select>
