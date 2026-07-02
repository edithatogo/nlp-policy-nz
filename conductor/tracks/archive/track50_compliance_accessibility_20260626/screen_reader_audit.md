# Track 50 Manual Screen Reader Audit

Date: 2026-07-02
Owner: codex_gpt5_engineer
Scope: `spaces/app.py`, `PRIVACY.md`, `.github/workflows/a11y-scan.yml`, and the Track 50 keyboard E2E coverage.

## Audit Boundary

This repo-side audit verifies the public Gradio Space semantics that NVDA and VoiceOver depend on: labelled inputs and outputs, visible keyboard focus, skip-link/main-content landmarks, reachable footer privacy notice, and automated axe/keyboard coverage. The current Codex environment cannot run VoiceOver, and no local NVDA installation is available here, so formal live assistive-technology certification remains an external launch gate.

## NVDA Review Checklist

| Area | Expected announcement/behaviour | Repo evidence | Result |
|---|---|---|---|
| Page entry | Page title announces `nlp-policy-nz Explorer`; skip link is first keyboard target. | `spaces/app.py` sets the Blocks title and renders `#skip-link`. | Pass |
| Main content | Activating the skip link moves context to `#main-content`. | `spaces/app.py` includes `#main-content`; CSS sets scroll margin. | Pass |
| Upload control | File picker has the explicit label `Upload a Parquet dataset`. | `gr.File(label="Upload a Parquet dataset")`. | Pass |
| Tabs | Overview, Corpus Statistics, Ontology Coverage, Graph and Vectors, Artifacts, Publication Protocol, and Dataset Browser are named tab stops. | Named `gr.Tab(...)` declarations in `spaces/app.py`. | Pass |
| Tables and JSON regions | Dataframes/JSON outputs have labels that describe their contents. | `label=` values on Gradio Dataframe, JSON, Plot, and Code components. | Pass |
| Dataset browser controls | Search query, max results, and Search button are labelled and keyboard operable. | `gr.Textbox`, `gr.Slider`, and `gr.Button` labels. | Pass |
| Privacy notice | Footer is reachable by keyboard and announces the privacy notice and policy link. | `#privacy-footer`; `tests/e2e/test_space_accessibility.py`. | Pass |

## VoiceOver Review Checklist

| Area | Expected announcement/behaviour | Repo evidence | Result |
|---|---|---|---|
| Safari/Chrome page title | Rotor exposes page title and content headings. | Blocks title and Markdown heading in `spaces/app.py`. | Pass |
| Keyboard traversal | Keyboard-only traversal reaches all controls and the privacy footer with no trap. | Playwright keyboard E2E test. | Pass |
| Focus visibility | Focus ring is visible for keyboard users. | `SPACE_CSS` defines `:focus-visible` outline. | Pass |
| Visualisations | Plot regions are labelled so screen reader users receive an accessible name even when chart internals are not fully narratable. | `gr.Plot(label=...)` and data-table alternatives in adjacent tabs. | Pass |
| Privacy/data handling | Footer and `PRIVACY.md` explain retention, PII, processors, and request path. | `PRIVACY_NOTICE` and `PRIVACY.md`. | Pass |

## Findings

No repo-side navigation or announcement defects were found. No code changes were required beyond the already implemented labels, focus styling, privacy footer, axe workflow, and keyboard-only E2E coverage.

## External Certification Gate

Before claiming formal public-sector accessibility certification, run live manual checks with:

- NVDA 2024 or newer on Windows with Chrome or Firefox.
- VoiceOver on current macOS with Safari.
- At least one keyboard-only walkthrough at 200% browser zoom.

Record any live assistive-technology defects as new follow-up work rather than reopening Track 50, unless they invalidate the committed compliance surface.
