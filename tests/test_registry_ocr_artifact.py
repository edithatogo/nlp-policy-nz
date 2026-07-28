from scripts.check_ocr_artifact_registry import check


def test_ocr_artifact_registry_contract() -> None:
    assert check() == []
