# Planning evidence — 2026-11-08

## Reviewed state

- Repository: `edithatogo/nlp-policy-nz`, default `master`, reviewed SHA `e2940f045ad2e065ef2b406843db10c7e850f0f6`.
- Clean isolated checkout before editing; no `AGENTS.md` or `CLAUDE.md` found in the checked tree. Read `CONTRIBUTING.md`, Conductor index/registry/workflow and the HDC profile before changes.
- Existing [#313](https://github.com/edithatogo/nlp-policy-nz/issues/313) is closed; `docs/source-profiles/hdc-medico-legal-profile.yaml` remains `design_profile_fixture_required`. The planning update does not equate issue closure with new runtime evidence.
- A direct authenticated open-pulls collection returned 35 dependency/CI update PRs, with no competing cognitive-autopsy/source-profile plan. An initial search endpoint returned no matches, so it was not used as the final inventory evidence. Those branches, manifests and lockfiles are untouched.
- Live [corpus repository metadata](https://api.github.com/repos/edithatogo/corpus-cases-medilegal-nz) reported `archived: false` and default branch `master`; this justifies correcting the older archived-status prose. Capture ownership remains with `archive-govt-nz`.

## Material gap and disposition

Existing source-trace schemas provide hashes and normalised-text spans; the HDC design has source separation and prohibited clinical outputs. The missing execution contract concerns immutable renditions/offset maps, explicit attribution/time candidates, scope-bound export and adapter qualification. Added seven bounded leaves and cross-links, preserving source/corpus/research/decision-tool ownership and optional dependency status.

No executable schema, package/lockfile, workflow, source payload or runtime code changes are included. The HDC YAML design profile remains unchanged. No model inference, new dependency installation, dataset download or publication occurred.

## Verification

- `git diff --check`: passed for tracked changes; new files separately checked for trailing whitespace and final newlines.
- Python documentation audit: 13 changed Markdown/JSON files, one parsed metadata JSON, 22 added/new relative Markdown links, seven unique acyclic work packages, and no runtime completion/qualification/release claims. Optional NLP-CA04 is not a hard prerequisite for another leaf.
- Existing HDC YAML checked byte-for-byte against the reviewed base and unchanged. No manifests, lockfiles, runtime code or workflows changed.
- An initial whole-file whitespace scan reported pre-existing Markdown spaces outside the patch. The audit was scoped to added/new lines, and the unrelated formatting was retained; the diff whitespace check already passed.
- The rcagent CAW references were checked against the coordinating work-package table; they are consumer integration points, not transferred clinical responsibilities.

Runtime tests, full `pixi run check`, model quality and data-release readiness are not claimed for this documentation-only change. No runtime was installed merely to test planning text. The implementation plan specifies the behaviour and compatibility tests required for each future leaf.
