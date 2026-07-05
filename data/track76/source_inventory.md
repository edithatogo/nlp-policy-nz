# Track 76 Source Inventory

- Schema version: 1.0
- Producer: nlp-policy-nz
- Fixture path: data/track76/source_inventory_fixtures.json
- Generated at: 2026-07-05T00:00:00+10:00
- Fixture bounded: True

## Claim boundary

This inventory is fixture-bounded and proves only offline source readiness; whole-corpus readiness still requires live crawling and rights confirmation.

## Status counts
- access_blocked: 1
- available: 2
- malformed: 1
- pdf_only: 1
- redirected: 1
- unavailable: 1

## Records

- track76-act-2026-001-html | act | available | nz/statutes/2026/1 | 9444430f1dee80db57f2adf62c2af8e653f3aa5e7ce8a537847bbdcdfe290bb4
- track76-reg-2026-014-html | regulation | available | nz/regulations/2026/14 | cf72301076bc352f180400382c67077e1717aae18e2d8014223f6cc375ebd164
- track76-amendment-2026-redirect | amendment | redirected | nz/amendments/2026/redirected-1 | 58a73d584d52aebe1ec451c2bba5959e10402f68f9719b73f608e1cd06fb3805
- track76-commencement-2026-pdf | commencement | pdf_only | nz/commencement/2026/9 | 0fb5eadbe9cda726b3a78552e73f43b22203089aa3346919e0738cd971a9c3ef
- track76-repeal-2026-malformed | repeal | malformed | nz/repeals/2026/4 | b98e676871881335642c2036d68e9c32d7e8b256e51fc70d969e3eb0a7bbb8ca
- track76-act-2026-access-blocked | act | access_blocked | nz/statutes/2026/blocked-1 | missing
- track76-reg-2026-unavailable | regulation | unavailable | nz/regulations/2026/unavailable-1 | missing

## Known gaps

- track76-amendment-2026-redirect:redirected: Redirected amendment source; follow the canonical target before claiming stability.
- track76-commencement-2026-pdf:pdf_only: PDF-only commencement source.
- track76-repeal-2026-malformed:malformed: Malformed repeal page requires parser repair.
- track76-act-2026-access-blocked:access_blocked: Source currently blocked to unauthenticated crawlers.
- track76-reg-2026-unavailable:unavailable: Source is not available yet.

## Live probe

- status: skipped
- skip reason: Live probing is opt-in and disabled by default.
