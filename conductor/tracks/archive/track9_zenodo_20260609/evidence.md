# Track 9 Evidence - Zenodo Archives and Release Workflows

Track 9 is complete for repo-side Zenodo archival and release workflow tooling.

Implemented surfaces:

- `src/nlp_policy_nz/integrations/zenodo.py` supports Sandbox and Production Zenodo API URLs, token selection, deposit creation, file upload, and publication.
- `src/nlp_policy_nz/integrations/zenodo_archive.py` wraps deposit creation, upload, publication, DOI lookup, and one-call `archive_to_zenodo` flows.
- `src/nlp_policy_nz/integrations/release.py` builds versioned release archives and publishes those archives through the Zenodo archiver.
- `src/nlp_policy_nz/integrations/__init__.py` exports the Zenodo archive and release helpers.
- `src/nlp_policy_nz/cli/main.py` exposes `archive-to-zenodo` and `release` commands.
- `.github/workflows/release.yml` defines tag-driven release workflow scaffolding.
- `scripts/release.sh` provides a local one-shot release helper with dry-run support.
- `README.md`, `conductor/product.md`, and `conductor/requirements.md` document the release and archival workflow.

Validation evidence:

- `tests/test_zenodo_archive.py` covers archiver behavior, DOI lookup, full mocked archive flows, missing files, and environment propagation.
- `tests/test_release.py` covers release archive creation, version metadata, archive contents, publish flow, and end-to-end mocked release behavior.
- `tests/test_cli.py` covers `archive-to-zenodo` and `release` parsing, handler dispatch, creator parsing, and error paths.
- `tests/integration/test_integrations_zenodo.py` covers low-level Zenodo payload and request wiring with mocked requests.
- `tests/test_provenance.py` covers Zenodo DOI/provenance linkage and release archive provenance metadata.
- The Track 9 Conductor contract test verifies this archived track keeps standard `index.md`, `spec.md`, `plan.md`, `metadata.json`, and `evidence.md` artifacts.

External gates:

- Live Sandbox or Production publication requires valid Zenodo credentials and an approved target release.
- Formal DOI publication is intentionally not claimed by this repo-side archive step.
- Fully automated semantic versioning, changelog, OSF, PyPI, and multi-registry publishing belong to Track 45.

