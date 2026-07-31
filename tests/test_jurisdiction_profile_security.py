from __future__ import annotations

import json
from pathlib import Path

import pytest

from nlp_policy_nz.config.jurisdiction_activation import (
    canonical_activation_registry_digest,
    load_profile_activation_registry,
)
from nlp_policy_nz.config.jurisdiction_profiles import (
    ProfileLoadError,
    ProfileRegistry,
    canonical_profile_digest,
    load_jurisdiction_profile,
    load_jurisdiction_profiles,
)


def _profile_payload(*, enabled: bool = True) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "profile_id": "foio-au-act",
        "profile_version": "0.1.0",
        "status": "enabled" if enabled else "disabled",
        "country": "AU",
        "jurisdiction_id": "AU-ACT",
        "jurisdiction_name": "Australian Capital Territory",
        "corpus": {
            "default_id": "corpus-au-act-foi",
            "id_pattern": "^corpus-au-act-[a-z0-9-]+$",
        },
        "capabilities": {
            "route_records": "enabled" if enabled else "disabled",
            "extract_assertions": "disabled",
            "export_ontology": "disabled",
        },
        "ontology_pin": (
            {
                "ontology_id": "synthetic-ontology",
                "ontology_version": "0.0.1",
                "ontology_sha256": "a" * 64,
            }
            if enabled
            else None
        ),
        "blockers": [] if enabled else ["Activation is not authorized."],
    }
    payload["profile_sha256"] = canonical_profile_digest(payload)
    return payload


def _registry_payload(profile: dict[str, object]) -> dict[str, object]:
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
    return payload


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_runtime_enforces_published_schema_before_semantics(tmp_path: Path) -> None:
    payload = _profile_payload()
    payload.pop("blockers")
    payload["profile_sha256"] = canonical_profile_digest(payload)
    path = tmp_path / "missing-required-field.json"
    _write_json(path, payload)

    with pytest.raises(ProfileLoadError, match="JSON Schema"):
        load_jurisdiction_profile(path)


def test_activation_registry_enforces_date_time_format(tmp_path: Path) -> None:
    profile = _profile_payload()
    registry = _registry_payload(profile)
    registry["grants"][0]["authorized_at"] = "not-a-date"  # type: ignore[index]
    registry["registry_sha256"] = canonical_activation_registry_digest(registry)
    path = tmp_path / "invalid-format.json"
    _write_json(path, registry)

    with pytest.raises(ProfileLoadError, match="date-time"):
        load_profile_activation_registry(
            path,
            expected_registry_sha256=str(registry["registry_sha256"]),
        )


def test_self_repin_cannot_activate_without_external_registry_pin(tmp_path: Path) -> None:
    profile_payload = _profile_payload()
    profile_path = tmp_path / "profile.json"
    _write_json(profile_path, profile_payload)
    profile = load_jurisdiction_profile(profile_path)

    with pytest.raises(ProfileLoadError, match="activation registry"):
        ProfileRegistry((profile,))

    registry_payload = _registry_payload(profile_payload)
    registry_path = tmp_path / "registry.json"
    _write_json(registry_path, registry_payload)
    with pytest.raises(ProfileLoadError, match="external pin"):
        load_profile_activation_registry(
            registry_path,
            expected_registry_sha256="f" * 64,
        )


def test_governed_resolution_requires_all_exact_selectors(tmp_path: Path) -> None:
    profile_payload = _profile_payload()
    profile_path = tmp_path / "profile.json"
    _write_json(profile_path, profile_payload)
    profile = load_jurisdiction_profile(profile_path)
    registry_payload = _registry_payload(profile_payload)
    registry_path = tmp_path / "registry.json"
    _write_json(registry_path, registry_payload)
    activation_registry = load_profile_activation_registry(
        registry_path,
        expected_registry_sha256=str(registry_payload["registry_sha256"]),
    )
    registry = ProfileRegistry((profile,), activation_registry=activation_registry)

    complete_selectors = {
        "version": "0.1.0",
        "profile_sha256": str(profile_payload["profile_sha256"]),
        "capability": "route_records",
    }
    for omitted in complete_selectors:
        incomplete = complete_selectors | {}
        incomplete.pop(omitted)
        with pytest.raises(TypeError):
            registry.resolve("foio-au-act", **incomplete)

    assert (
        registry.resolve(
            "foio-au-act",
            version="0.1.0",
            profile_sha256=str(profile_payload["profile_sha256"]),
            capability="route_records",
        ).status
        == "routed"
    )
    assert (
        registry.resolve(
            "foio-au-act",
            version="9.9.9",
            profile_sha256=str(profile_payload["profile_sha256"]),
            capability="route_records",
        ).status
        == "abstained"
    )
    assert (
        registry.resolve(
            "foio-au-act",
            version="0.1.0",
            profile_sha256="f" * 64,
            capability="route_records",
        ).status
        == "abstained"
    )
    assert (
        registry.resolve(
            "foio-au-act",
            version="0.1.0",
            profile_sha256=str(profile_payload["profile_sha256"]),
            capability="unknown",
        ).status
        == "abstained"
    )


def test_committed_activation_registry_has_no_grants() -> None:
    registry_path = Path("config/jurisdiction-activation-registry.json")
    payload = json.loads(registry_path.read_text())
    assert payload["grants"] == []
    assert payload["registry_sha256"] == canonical_activation_registry_digest(payload)
    registry = load_profile_activation_registry(
        registry_path,
        expected_registry_sha256=str(payload["registry_sha256"]),
    )
    assert registry.grants == ()
    profiles = load_jurisdiction_profiles(
        "config/jurisdictions",
        activation_registry_path=registry_path,
        expected_activation_registry_sha256=str(payload["registry_sha256"]),
    )
    assert all(profile.status.value == "disabled" for profile in profiles.profiles)


def test_published_and_packaged_schemas_are_identical() -> None:
    for filename in (
        "jurisdiction_profile.schema.json",
        "jurisdiction_activation_registry.schema.json",
    ):
        published = json.loads(Path("schemas", filename).read_text())
        packaged = json.loads(Path("src/nlp_policy_nz/config/schemas", filename).read_text())
        assert published == packaged
