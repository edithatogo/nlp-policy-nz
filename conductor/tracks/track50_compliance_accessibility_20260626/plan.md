# Track 50: Public Sector Compliance & Accessibility

**Dependencies**: Tracks 36, 44, 46
**Parallelization Node**: Compliance & Governance
**Status**: Planned

## Implementation Plan

| # | Task | Status | Owner |
|---|------|--------|-------|
| 1 | Run automated WCAG audit (axe-core via Playwright) against the Gradio Space; fix all critical/serious violations | [ ] | conductor_orchestrator |
| 2 | Implement keyboard navigation: tab order, skip links, focus trapping in modals, escape-to-close | [ ] | conductor_orchestrator |
| 3 | Add ARIA labels to all form inputs, buttons, data tables, and visualisation canvases in the Space | [ ] | conductor_orchestrator |
| 4 | Verify contrast ratios: adjust Space theme colours to meet 4.5:1 minimum; add colour-blind safe palette | [ ] | conductor_orchestrator |
| 5 | Write `PRIVACY.md` documenting data retention, PII handling, deletion process, and third-party processors | [ ] | conductor_orchestrator |
| 6 | Add privacy notice to Gradio Space footer; add data subject request contact email | [ ] | conductor_orchestrator |
| 7 | Create CI workflow `a11y-scan.yml` that runs axe-core audit against deployed Space URL on every deploy | [ ] | conductor_orchestrator |
| 8 | Conduct manual screen reader audit (NVDA + VoiceOver); fix any navigation or announcement issues found | [ ] | conductor_orchestrator |
| 9 | Add keyboard-only navigation test to E2E tests (Playwright): tab through all controls, verify no keyboard traps | [ ] | conductor_orchestrator |

## Evidence Boundary

Gradio Space source code with accessibility fixes, PRIVACY.md, axe-core scan results, and manual audit report satisfy repo-side evidence. Formal WCAG certification requires external auditor.
