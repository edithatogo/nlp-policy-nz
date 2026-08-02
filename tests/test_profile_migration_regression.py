from __future__ import annotations

from hashlib import sha256

from nlp_policy_nz.extraction.foio_au_adapter import (
    AustralianJurisdiction,
    build_australian_archive_bundle,
    render_australian_archive_bundle_json,
)
from nlp_policy_nz.extraction.foio_nz_adapter import (
    build_new_zealand_archive_bundle,
    render_new_zealand_archive_bundle_json,
)
from tests.test_foio_au_adapter import (
    _record as australian_record,
    _snapshot as australian_snapshot,
)
from tests.test_foio_nz_adapter import (
    _record as new_zealand_record,
    _snapshot as new_zealand_snapshot,
)

EXPECTED_BUNDLE_BYTES = {
    "nz": ("9efb833761ac7f999ccd37c4178c98d1145774130a2fb44d388c9ebfe68a03c7", 2309),
    "au-cth": ("038a7ed5dddfc099e750231ad57458408fb25644d3adb7105028314980f5a237", 2241),
    "au-nsw": ("4a951ea6760a7c4b833edb13614f4888009f011becf11ded95064372374e8bfa", 2241),
}


def _digest(rendered: str) -> tuple[str, int]:
    encoded = rendered.encode("utf-8")
    return sha256(encoded).hexdigest(), len(encoded)


def test_existing_nz_cth_and_nsw_adapter_bytes_are_unchanged() -> None:
    rendered = {
        "nz": render_new_zealand_archive_bundle_json(
            build_new_zealand_archive_bundle(
                [new_zealand_record()],
                new_zealand_snapshot(),
            )
        ),
        "au-cth": render_australian_archive_bundle_json(
            build_australian_archive_bundle(
                [australian_record("cth", jurisdiction="Cth")],
                australian_snapshot(AustralianJurisdiction.COMMONWEALTH),
            )
        ),
        "au-nsw": render_australian_archive_bundle_json(
            build_australian_archive_bundle(
                [australian_record("nsw", jurisdiction="NSW")],
                australian_snapshot(AustralianJurisdiction.NSW),
            )
        ),
    }

    assert {name: _digest(value) for name, value in rendered.items()} == EXPECTED_BUNDLE_BYTES
