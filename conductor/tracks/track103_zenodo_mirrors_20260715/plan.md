# Plan

## Phase 1: Repository contract

- [x] Add version-aligned Zenodo metadata generation.
- [x] Add unverified-by-default DOI mirror manifest.
- [x] Include release metadata and mirror evidence in release artifacts.
- [x] Add focused tests and lint validation.

## Phase 2: External acceptance

- [ ] Verify GitHub-to-Zenodo archiving for a real tagged release.
- [ ] Record the live version DOI, concept DOI, record URL, and verification timestamp.
- [ ] Close the issue only after the live record is accessible and the manifest is updated.

## Acceptance boundary

Repository-side generation is complete. DOI publication remains an external
gate and is intentionally not claimed by the committed unverified manifest.
