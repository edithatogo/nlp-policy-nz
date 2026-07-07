from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from nlp_policy_nz.capabilities import (
    CapabilityClassification,
    CapabilityEntry,
    CapabilityMaturity,
    CapabilityRegistry,
    CapabilitySurface,
    DEFAULT_CAPABILITY_REGISTRY,
    dump_capability_registry,
    load_capability_registry,
    validate_capability_entries,
    validate_capability_registry,
)


def test_default_registry_covers_current_and_future_surfaces() -> None:
    registry = validate_capability_registry(DEFAULT_CAPABILITY_REGISTRY)

    assert registry.surfaces() == (
        CapabilitySurface.CLI,
        CapabilitySurface.API,
        CapabilitySurface.SDK,
        CapabilitySurface.MCP,
    )
    assert registry.missing_surfaces() == ()
    assert len(registry.ids()) == len(set(registry.ids()))
    assert all(entry.id == entry.id.lower() for entry in registry.entries)
    assert all(entry.required_fields == tuple(dict.fromkeys(entry.required_fields)) for entry in registry.entries)


def test_duplicate_stable_ids_are_rejected() -> None:
    base = CapabilityEntry(
        id="sdk.demo",
        surface=CapabilitySurface.SDK,
        name="Demo helper",
        summary="Minimal helper for duplicate-ID validation.",
        maturity=CapabilityMaturity.CURRENT,
        classification=CapabilityClassification.PUBLIC,
        required_fields=("input_path",),
        implementation_ref="src/nlp_policy_nz/capabilities.py#demo",
        contract_kind="python_function",
    )
    duplicate = replace(base, name="Duplicate demo helper")

    with pytest.raises(ValueError, match="Duplicate capability IDs"):
        CapabilityRegistry(entries=(base, duplicate))


def test_invalid_stable_ids_are_rejected() -> None:
    bad = CapabilityEntry.__new__(CapabilityEntry)
    object.__setattr__(bad, "id", "SDK.Demo")
    object.__setattr__(bad, "surface", CapabilitySurface.SDK)
    object.__setattr__(bad, "name", "Bad helper")
    object.__setattr__(bad, "summary", "Uppercase identifiers are rejected.")
    object.__setattr__(bad, "maturity", CapabilityMaturity.CURRENT)
    object.__setattr__(bad, "classification", CapabilityClassification.PUBLIC)
    object.__setattr__(bad, "required_fields", ("input_path",))
    object.__setattr__(bad, "implementation_ref", "src/nlp_policy_nz/capabilities.py#demo")
    object.__setattr__(bad, "contract_kind", "python_function")
    object.__setattr__(bad, "aliases", ())

    with pytest.raises(ValueError, match="stable"):
        validate_capability_entries((bad,))


def test_registry_round_trip_through_json_loader(tmp_path: Path) -> None:
    path = tmp_path / "capabilities.json"
    dump_capability_registry(DEFAULT_CAPABILITY_REGISTRY, path)

    loaded = load_capability_registry(path)

    assert loaded == DEFAULT_CAPABILITY_REGISTRY
    assert path.read_text(encoding="utf-8").startswith("{\n  \"entry_count\":")
