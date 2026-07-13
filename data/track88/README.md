# Track 88 Held-Out Structure Annotations

This directory contains metadata-only evaluation design for historical New Zealand
parliamentary structure reconstruction. It deliberately contains no corpus text,
OCR payload, or model output. Volume/page identifiers are resolved by the cloud
archive workflow before evaluation.

The strata cover year bands, page geometry, and parliamentary document types. Gold
annotations must be created outside the training corpus, with source spans pointing
to immutable page/block/token identifiers. Promotion is fail-closed when a span or
review decision cannot be reproduced.
