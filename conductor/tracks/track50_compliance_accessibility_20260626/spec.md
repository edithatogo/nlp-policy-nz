# Track 50: Public Sector Compliance & Accessibility

**Dependencies**: Tracks 36, 44, 46
**Parallelization Node**: Compliance & Governance
**Status**: Planned

## Goal

Ensure the HF Gradio Space and all public-facing outputs meet NZ government accessibility standards and NZ Privacy Act 2020 data governance requirements.

## Scope

### 1. WCAG 2.1 AA / NZ Web Accessibility Standard
- Contrast ratio compliance (4.5:1 text, 3:1 large text)
- Keyboard navigation: all interactive elements focusable and operable
- Screen reader labels for all form elements, tables, and visualisations
- Focus indicators visible on all interactive elements
- ARIA landmarks and roles correct
- Text resize: no content loss at 200% zoom
- Error identification: form validation messages

### 2. Privacy Act 2020 Compliance
- Data flow audit: identify PII in corpus (MP names, electorate data, spoken content)
- Data retention policy documented (how long is data stored, how to delete)
- Data subject request mechanism (how to request deletion or correction)
- Privacy notice in the Gradio Space footer
- Third-party data processor agreements (HF, Zenodo, OSF)

### 3. Accessibility Testing
- Add accessibility check step to CI (axe-core or Pa11y for Gradio Space)
- Screen reader testing with NVDA (Windows) and VoiceOver (macOS)
- Manual keyboard-only navigation audit
- Colour-blind safe palette verification (all visualisations)

## Acceptance Criteria

- [ ] Gradio Space passes automated axe-core audit with zero critical/serious violations
- [ ] All interactive elements keyboard-accessible (tab order, focus trap, enter/escape handling)
- [ ] Screen reader correctly announces all content and state changes
- [ ] Contrast ratios meet WCAG AA thresholds throughout the Space
- [ ] Privacy notice visible in Gradio Space footer
- [ ] Data retention policy documented in `PRIVACY.md`
- [ ] Data subject request process documented with contact email
- [ ] CI runs accessibility scan on deploy
