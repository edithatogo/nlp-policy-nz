# Publication gates

Green repository CI proves repository checks only. It does not prove that an
external registry accepted a release or that a DOI, dataset, package, or OSF
record exists.

| Registry | Sandbox/test gate | Production gate | Required secret(s) |
| --- | --- | --- | --- |
| Hugging Face | Use a test repository or dry-run plan; verify the staged manifest and card. | Explicit target repository, reviewed manifest, and successful authenticated workflow. | `HF_TOKEN` and target IDs such as `HF_ARCHIVE_DATASET_ID` |
| Zenodo | Use `sandbox.zenodo.org`; verify metadata and files without publishing a production DOI. | Explicit production endpoint, reviewed deposit, and human approval before publish. | `ZENODO_SANDBOX_TOKEN` or `ZENODO_PRODUCTION_TOKEN` |
| PyPI | Build and inspect the wheel; use TestPyPI for an upload rehearsal. | Tag/release workflow with reviewed artifacts and production credentials. | `PYPI_API_TOKEN` |
| OSF | Prepare metadata and an upload plan against a test or explicitly selected project. | Explicit project/component, reviewed files, and authenticated release action. | `OSF_TOKEN` |

Publication workflows are opt-in and credential-gated. A local command, green
CI run, staged artifact, or sandbox record must not be described as production
publication. The release workflow and Track 45 publication protocol remain the
authoritative operational references.
