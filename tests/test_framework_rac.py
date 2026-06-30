from nlp_policy_nz.universal_framework_v3 import (
    FrameworkConfig,
    MetaExtensionRegistry,
    TargetSchemaEmitter,
    run_framework,
)


def test_catala_dsl_emission():
    # Setup framework config with Catala-DSL
    config = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="Catala-DSL",
    )

    raw_xml = '<section id="sec-12" title="Application for Grant"><para>An applicant must apply to the Chief Executive. Subsection (1) does not apply if the applicant is a registered member.</para></section>'

    doc = run_framework(config, raw_xml)

    # Verify metadata registry and emitter
    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)
    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)

    output = emitter.emit(doc)

    assert "declaration structure Sec12" in output
    assert "input applicant: boolean" in output
    assert "rule Sec12" in output


def test_akoma_ntoso_rac_features():
    # Setup framework config with Akoma-Ntoso
    config = FrameworkConfig(
        country="New Zealand",
        jurisdiction="National Parliament & PCO Legislative Corpus",
        source_data_format="XML",
        target_schema_standard="Akoma-Ntoso",
    )

    # Include some Te Reo Maori words (e.g. Kāwanatanga) and definition pattern (e.g. "term means")
    raw_xml = '<section id="sec-5" title="Interpretation"><para>“Kāwanatanga” means governance. An applicant must apply.</para></section>'

    doc = run_framework(config, raw_xml)

    country_key, schema_key, chunk_id_key = MetaExtensionRegistry.register(config)
    emitter = TargetSchemaEmitter(config, country_key, schema_key, chunk_id_key)

    output = emitter.emit(doc)

    # Māori Language Guard phrase tag with refersTo ontology check
    assert '<phrase xml:lang="mi" refersTo="#tikanga_kawanatanga">' in output
    # Definition tag check
    assert "<definition>" in output or "Kāwanatanga" in output
    # References and TLCConcept tags (W3C PROV-O lineage) check
    assert '<references source="#nlp_policy_nz">' in output
    assert '<TLCConcept id="prov_pipeline_version"' in output
    # LegalRuleML tag check
    assert "<legalRuleML" in output
    assert "<Rule" in output
