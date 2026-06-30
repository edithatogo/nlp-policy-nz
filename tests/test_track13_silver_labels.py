"""Tests for Track 13 silver-label triangulation."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.training.track13_silver import (
    OntologyConcept,
    SilverVote,
    aggregate_silver_votes,
    build_provider_prompt,
    discover_provider_availability,
    make_target_record,
    match_ontology_concepts,
    ontology_bridge_vote,
)


def test_silver_manifest_prefers_human_labelled_calibration_sources() -> None:
    manifest = json.loads(
        Path(
            "conductor/tracks/archive/track13_argument_stance_20260613/silver_label_manifest.json",
        ).read_text(encoding="utf-8")
    )

    sources = manifest["human_labelled_calibration_sources"]
    assert any(source["human_labelled"] is True for source in sources)
    assert {source["id"] for source in sources} >= {
        "ukp_argumentative_essays",
        "iam_integrated_argument_mining",
        "mining_legal_arguments_echr",
    }
    assert all(source.get("sources") for source in sources)
    assert (
        "data/track13/calibration/human_calibration_votes.jsonl"
        in manifest["calibration_artifacts"]
    )
    assert manifest["quality_gates"][0]["id"] == "external_human_calibration_source_present"


def test_calibration_vote_files_cover_all_configured_sources() -> None:
    manifest = json.loads(
        Path("data/track13/calibration/calibration_manifest.json").read_text(encoding="utf-8")
    )
    allowed = {
        "claim_label": {"claim", "major_claim", "non_argument"},
        "premise_label": {"premise", "evidence", "none"},
        "relation_label": {"support", "attack", "none"},
        "source_type": {"human_calibration", "human_in_loop_calibration"},
    }

    source_ids = {artifact["id"] for artifact in manifest["artifacts"]}
    assert {
        "ukp_argumentative_essays",
        "iam_integrated_argument_mining",
        "mining_legal_arguments_echr",
        "lamus_legal_argument_mining",
        "combined_human_calibration",
    } <= source_ids

    for artifact in manifest["artifacts"]:
        rows = [
            json.loads(line)
            for line in Path(artifact["path"]).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == artifact["rows"]
        for row in rows:
            assert row["record_id"]
            assert row["text"]
            assert row["source_type"] in allowed["source_type"]
            assert row["claim_label"] in allowed["claim_label"]
            assert row["premise_label"] in allowed["premise_label"]
            assert row["relation_label"] in allowed["relation_label"]
            assert 0 <= float(row["confidence"]) <= 1
            assert row["source_url"].startswith("http")


def test_provider_availability_uses_configured_commands() -> None:
    availability = discover_provider_availability(
        {
            "present": ("python",),
            "missing": ("definitely-not-a-track13-provider",),
        }
    )

    by_provider = {item.provider: item for item in availability}
    assert by_provider["present"].available
    assert by_provider["present"].executable
    assert not by_provider["missing"].available


def test_provider_labelling_plan_includes_installed_and_api_providers() -> None:
    plan = json.loads(
        Path(
            "conductor/tracks/archive/track13_argument_stance_20260613/"
            "ai_provider_labelling_plan.json",
        ).read_text(encoding="utf-8")
    )

    installed = {provider["provider"] for provider in plan["installed_local_providers"]}
    assert installed >= {"cline", "opencode", "mimo", "agy", "agent"}
    assert {provider["provider"] for provider in plan["configured_api_providers"]} == {
        "openrouter",
        "nvidia_nim",
    }
    assert "silver labels only" in plan["acceptance"]["gold_label_warning"]


def test_track13_model_recommendations_keep_classifier_and_adjudicator_roles_separate() -> None:
    plan = json.loads(
        Path(
            "conductor/tracks/archive/track13_argument_stance_20260613/"
            "ai_provider_labelling_plan.json",
        ).read_text(encoding="utf-8")
    )

    recommendations = plan["model_recommendations"]
    classifier_models = {item["model"] for item in recommendations["local_classifier_baselines"]}
    adjudicator_models = {item["model"] for item in recommendations["silver_label_adjudicators"]}

    assert "isaacus/emubert" in classifier_models
    assert "nlpaueb/legal-bert-base-uncased" in classifier_models
    assert "Equall/Saul-7B-Instruct-v1" in adjudicator_models
    assert "isaacus/open-australian-legal-llm" in adjudicator_models
    assert "gold labels" in recommendations["silver_label_adjudicators"][0]["notes"]
    assert "NZ-legislation fine-tuning" in recommendations["follow_up_issue"]


def test_ontology_triangulation_manifest_links_hpo_umls_and_snomed() -> None:
    manifest = json.loads(
        Path(
            "conductor/tracks/archive/track13_argument_stance_20260613/"
            "ontology_triangulation_manifest.json",
        ).read_text(encoding="utf-8")
    )
    silver_manifest = json.loads(
        Path(
            "conductor/tracks/archive/track13_argument_stance_20260613/silver_label_manifest.json",
        ).read_text(encoding="utf-8")
    )

    ontologies = {item["id"] for item in manifest["crosswalk_ontologies"]}
    assert {"umls", "snomed_ct", "mesh"} <= ontologies
    assert manifest["silver_vote_policy"]["source_type"] == "weak_rule"
    assert (
        "must not be represented as human labels"
        in manifest["silver_vote_policy"]["gold_label_warning"]
    )
    assert silver_manifest["ontology_triangulation_sources"][0]["id"] == (
        "ontology_bridge_hpo_umls_snomed"
    )


def test_track13_target_record_and_provider_prompt_are_schema_stable() -> None:
    record = make_target_record("rec-1", "  Therefore, the bill should pass.  ")
    prompt = build_provider_prompt(record["record_id"], record["text"])

    assert record == {"record_id": "rec-1", "text": "Therefore, the bill should pass."}
    assert "Return exactly one JSON object" in prompt
    assert "claim_label" in prompt
    assert "premise_label" in prompt
    assert "relation_label" in prompt
    assert "source_type='ai_provider'" in prompt


def test_ontology_bridge_creates_weak_rule_vote_only() -> None:
    concepts = [
        OntologyConcept(
            concept_id="UMLS:C0024031",
            label="low back pain",
            ontology="UMLS",
            hpo_id="HP:0003419",
            xrefs=("SNOMEDCT_US:279039007",),
        )
    ]

    matches = match_ontology_concepts(
        "The submission describes low back pain treatment access.",
        concepts,
    )
    vote = ontology_bridge_vote(
        "health-1",
        "The submission describes low back pain treatment access.",
        concepts,
    )

    assert matches == concepts
    assert vote is not None
    assert vote.provider == "ontology_bridge"
    assert vote.source_type == "weak_rule"
    assert vote.weight <= 0.25


def test_silver_consensus_accepts_human_calibrated_two_model_agreement() -> None:
    votes = [
        SilverVote(
            "rec-1",
            "ukp_argumentative_essays",
            "human_calibration",
            "claim",
            "premise",
            "support",
        ),
        SilverVote(
            "rec-1",
            "cline",
            "ai_provider",
            "claim",
            "premise",
            "support",
            confidence=0.9,
        ),
        SilverVote(
            "rec-1",
            "opencode",
            "ai_provider",
            "claim",
            "premise",
            "support",
            confidence=0.85,
        ),
        SilverVote(
            "rec-1",
            "weak_rule",
            "weak_rule",
            "claim",
            "premise",
            "support",
            confidence=0.6,
        ),
    ]

    consensus = aggregate_silver_votes("rec-1", votes)

    assert consensus.accepted
    assert not consensus.disagreement
    assert consensus.claim_label == "claim"
    assert consensus.premise_label == "premise"
    assert consensus.relation_label == "support"
    assert consensus.consensus_score >= 0.67
    assert "ukp_argumentative_essays" in consensus.sources


def test_silver_consensus_routes_low_agreement_to_disagreement_queue() -> None:
    votes = [
        SilverVote("rec-2", "cline", "ai_provider", "claim", "premise", "support"),
        SilverVote("rec-2", "opencode", "ai_provider", "non_argument", "none", "none"),
        SilverVote("rec-2", "mimo", "ai_provider", "claim", "none", "attack"),
    ]

    consensus = aggregate_silver_votes("rec-2", votes)

    assert not consensus.accepted
    assert consensus.disagreement
    assert (
        consensus.to_json_record("Because housing costs rose, the bill should pass.")[
            "silver_label"
        ]
        is False
    )
