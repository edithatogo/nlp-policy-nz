from scripts.check_registry_readiness import check


def test_registry_readiness_contract():
    assert check() == []
