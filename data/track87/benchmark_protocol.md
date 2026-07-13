# Track 87 Benchmark Protocol

The candidate engines are evaluated on held-out historical-page cohorts before any engine is promoted. The fixture metadata covers single-column, multi-column, table, marginalia, and year-band variation; source images and text are supplied only to cloud benchmark workers.

Each result reports:

- character error rate and word error rate;
- token disagreement and retained token alignments;
- layout-region and reading-order accuracy;
- table-region accuracy;
- confidence calibration error;
- cost per page and pages per second.

The promotion result is fail-closed: all configured thresholds must pass. A candidate with no immutable model and container digests remains `adapter_contract_only`, even if its fixture score is good. Benchmark outputs must include the engine version, model digest, container digest, source fixture manifest, and pipeline version.
