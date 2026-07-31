from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from nlp_policy_nz.config.jurisdiction_activation import (
    ProfileActivationRegistry,
    canonical_activation_registry_digest,
)
from nlp_policy_nz.config.jurisdiction_profiles import (
    JurisdictionProfile,
    ProfileLoadError,
    ProfileRegistry,
    canonical_profile_digest,
    load_jurisdiction_profile,
    load_jurisdiction_profiles,
)

SCAFFOLD_PROFILE_IDS = {
    "foio-au-act",
    "foio-au-nt",
    "foio-au-qld",
    "foio-au-sa",
    "foio-au-tas",
    "foio-au-vic",
    "foio-au-wa",
}


def _profile_payload(*, profile_id: str = "synthetic-test") -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "profile_id": profile_id,
        "profile_version": "0.1.0",
        "status": "enabled",
        "country": "ZZ",
        "jurisdiction_id": "ZZ-TEST",
        "jurisdiction_name": "Synthetic test jurisdiction",
        "corpus": {
            "default_id": "corpus-zz-test",
            "id_pattern": "^corpus-zz-[a-z0-9-]+$",
        },
        "capabilities": {
            "route_records": "enabled",
            "extract_assertions": "unsupported",
            "export_ontology": "disabled",
        },
        "ontology_pin": {
            "ontology_id": "synthetic-ontology",
            "ontology_version": "0.0.1",
            "ontology_sha256": "a" * 64,
        },
        "blockers": [],
    }
    payload["profile_sha256"] = canonical_profile_digest(payload)
    return payload


def _activation_registry(profile: dict[str, object]) -> ProfileActivationRegistry:
    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "registry_id": "jurisdiction-profile-activations",
        "registry_version": "1.0.0",
        "grants": [
            {
                "profile_id": profile["profile_id"],
                "profile_version": profile["profile_version"],
                "profile_sha256": profile["profile_sha256"],
                "capability": "route_records",
                "authorization_sha256": "b" * 64,
                "authorized_at": "2026-07-31T10:00:00Z",
            }
        ],
    }
    payload["registry_sha256"] = canonical_activation_registry_digest(payload)
    return ProfileActivationRegistry.model_validate(payload)


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_loader_accepts_strict_hash_pinned_json_and_yaml(
    tmp_path: Path,
    suffix: str,
) -> None:
    payload = _profile_payload()
    path = tmp_path / f"profile{suffix}"
    if suffix == ".json":
        path.write_text(json.dumps(payload), encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")

    loaded = load_jurisdiction_profile(
        path,
        expected_profile_id="synthetic-test",
        expected_version="0.1.0",
        expected_sha256=str(payload["profile_sha256"]),
    )

    assert loaded.profile_id == "synthetic-test"
    assert loaded.country == "ZZ"
    assert loaded.corpus.default_id == "corpus-zz-test"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"schema_version": "2.0.0"}, "schema_version"),
        ({"profile_id": "UNKNOWN"}, "profile_id"),
        ({"profile_version": "latest"}, "profile_version"),
        ({"country": "zzz"}, "country"),
        ({"unexpected": True}, "extra"),
    ],
)
def test_profile_schema_rejects_unknown_or_malformed_fields(
    mutation: dict[str, object],
    message: str,
) -> None:
    payload = _profile_payload()
    payload.update(mutation)
    payload["profile_sha256"] = canonical_profile_digest(payload)

    with pytest.raises(ValidationError, match=message):
        JurisdictionProfile.model_validate(payload)


def test_loader_rejects_duplicate_keys_and_self_pin_mismatch(tmp_path: Path) -> None:
    duplicate_json = tmp_path / "duplicate.json"
    duplicate_json.write_text(
        '{"schema_version":"1.0.0","schema_version":"1.0.0"}',
        encoding="utf-8",
    )
    with pytest.raises(ProfileLoadError, match="duplicate key"):
        load_jurisdiction_profile(duplicate_json)

    duplicate_yaml = tmp_path / "duplicate.yaml"
    duplicate_yaml.write_text(
        "schema_version: 1.0.0\nschema_version: 1.0.0\n",
        encoding="utf-8",
    )
    with pytest.raises(ProfileLoadError, match="duplicate key"):
        load_jurisdiction_profile(duplicate_yaml)

    payload = _profile_payload()
    payload["profile_sha256"] = "f" * 64
    mismatched = tmp_path / "mismatched.json"
    mismatched.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ProfileLoadError, match="self-pin"):
        load_jurisdiction_profile(mismatched)


def test_registry_resolution_fails_closed_for_every_untrusted_selector() -> None:
    payload = _profile_payload()
    profile = JurisdictionProfile.model_validate(payload)
    registry = ProfileRegistry((profile,), activation_registry=_activation_registry(payload))

    selectors = {
        "version": "0.1.0",
        "profile_sha256": str(payload["profile_sha256"]),
        "capability": "route_records",
    }
    assert registry.resolve("missing", **selectors).status == "abstained"
    assert (
        registry.resolve("synthetic-test", **(selectors | {"version": "9.9.9"})).status
        == "abstained"
    )
    assert (
        registry.resolve("synthetic-test", **(selectors | {"profile_sha256": "f" * 64})).status
        == "abstained"
    )
    assert (
        registry.resolve("synthetic-test", **(selectors | {"capability": "unknown"})).status
        == "abstained"
    )
    assert (
        registry.resolve(
            "synthetic-test", **(selectors | {"capability": "extract_assertions"})
        ).status
        == "abstained"
    )
    routed = registry.resolve("synthetic-test", **selectors)
    assert routed.status == "routed"
    assert routed.profile == profile


def test_repository_scaffolds_are_disabled_and_contain_no_legal_markers() -> None:
    registry = load_jurisdiction_profiles(Path("config/jurisdictions"))

    assert {profile.profile_id for profile in registry.profiles} == SCAFFOLD_PROFILE_IDS
    for profile in registry.profiles:
        assert profile.status == "disabled"
        assert profile.ontology_pin is None
        assert set(profile.capabilities.values()) == {"disabled"}
        assert profile.blockers
        assert (
            registry.resolve(
                profile.profile_id,
                version=profile.profile_version,
                profile_sha256=profile.profile_sha256,
                capability="route_records",
            ).status
            == "abstained"
        )


def test_directory_loader_rejects_duplicate_profile_versions(tmp_path: Path) -> None:
    payload = _profile_payload()
    for name in ("one.json", "two.yaml"):
        path = tmp_path / name
        if path.suffix == ".json":
            path.write_text(json.dumps(payload), encoding="utf-8")
        else:
            path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    with pytest.raises(ProfileLoadError, match="duplicate profile/version"):
        load_jurisdiction_profiles(tmp_path)
