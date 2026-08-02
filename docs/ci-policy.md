# CI policy

Pull requests use the fast lane plus security, documentation, container, and
publication-boundary checks. The full operating-system and Python matrix runs
on master and nightly schedule; experimental Python probes are informative and
are not release or adoption evidence.

The self-healing workflow may prepare a report after a failed CI run, but it
cannot open a healing PR unless the source PR has the `self-heal-approved`
label. Maintainers review the report and label the PR explicitly when an
automated repair is appropriate.

Dependabot owns dependency update pull requests. Renovate configuration is
retained for repository compatibility, but it must not be enabled for the same
dependency scope without an explicit ownership decision.
