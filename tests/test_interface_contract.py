"""Tests for the shared interface contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from nlp_policy_nz.interface_contract import (
    DEFAULT_INTERFACE_CONTRACT,
    AuthRequirement,
    CapabilityRecord,
    InterfaceContract,
    SideEffectLevel,
    SurfaceKind,
    capability_inventory,
    contract_summary,
    load_interface_contract_json,
    surface_inventory,
    write_interface_contract_json,
)


def test_default_contract_has_expected_surfaces() -> None:
    contract = DEFAULT_INTERFACE_CONTRACT

    assert contract.contract_id == "nlp-policy-nz.interface-contract.v1"
    assert contract_summary(contract)["capability_count"] >= 10
    inventory = surface_inventory(contract)
    assert "cli" in inventory
    assert "api" in inventory
    assert "sdk" in inventory
    assert "report" in inventory
    assert "mcp" in inventory


def test_capabilities_are_unique_and_valid() -> None:
    contract = DEFAULT_INTERFACE_CONTRACT
    contract.validate()
    ids = [record.capability_id for record in contract.capabilities]
    assert len(ids) == len(set(ids))


def test_contract_rejects_duplicate_ids() -> None:
    record = CapabilityRecord(
        capability_id="dup.one",
        title="One",
        surface=SurfaceKind.CLI,
        owner_module="module.one",
        description="one",
        side_effect=SideEffectLevel.READ_ONLY,
    )
    with pytest.raises(ValueError, match="unique"):
        InterfaceContract(
            contract_id="x",
            contract_version="v1",
            generated_from="tests",
            capabilities=(record, record),
        )


def test_contract_requires_auth_scope_for_mutating_capability() -> None:
    record = CapabilityRecord(
        capability_id="bad.write",
        title="Bad write",
        surface=SurfaceKind.API,
        owner_module="module.bad",
        description="bad",
        side_effect=SideEffectLevel.LOCAL_WRITE,
        auth_requirement=AuthRequirement.REQUIRED,
        auth_scope=None,
    )
    contract = InterfaceContract(
        contract_id="x",
        contract_version="v1",
        generated_from="tests",
        capabilities=(record,),
    )
    with pytest.raises(ValueError, match="auth scope"):
        contract.validate()


def test_round_trip_json(tmp_path: Path) -> None:
    output = tmp_path / "interface-contract.json"
    written = write_interface_contract_json(DEFAULT_INTERFACE_CONTRACT, output)
    loaded = load_interface_contract_json(written)

    assert loaded.contract_id == DEFAULT_INTERFACE_CONTRACT.contract_id
    assert len(loaded.capabilities) == len(DEFAULT_INTERFACE_CONTRACT.capabilities)
    assert capability_inventory(loaded)[0]["capability_id"].startswith("cli.")
