# Track 93 Evidence

- `src/nlp_policy_nz/extraction/foio_promotion.py` models separate NZ/archive,
  Commonwealth, and NSW promotion lanes and fails closed on missing rights,
  immutable source/model identity, held-out records, or review evidence.
- Focused promotion tests cover disjoint held-out IDs, rights evidence,
  immutable pins, independent review, and no-promotion output.
- Issue #129 was closed after the promotion-evidence scaffold merged in PR #141.

No real rights-cleared records, independent reviewer identities, adjudication
signatures, or empirical metrics are present; this archive records a contract
closeout, not empirical promotion.
