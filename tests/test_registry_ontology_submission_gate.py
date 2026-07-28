from scripts.check_ontology_submission_gate import check


def test_ontology_submission_gate_contract() -> None:
    assert check() == []
