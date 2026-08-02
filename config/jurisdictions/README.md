# Jurisdiction profiles

Profiles are versioned JSON contracts. Each profile contains an explicit
`profile_id`, country, corpus prefix, adapter name, version, and SHA-256 digest
over the unsigned fields. `ProfileLoader` fails closed for unknown IDs,
malformed profiles, and digest changes; it never silently falls back to NZ.

The shipped profiles are routing contracts only. They do not establish
cross-jurisdiction equivalence, rights clearance, or empirical adoption.
