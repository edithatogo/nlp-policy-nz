from nlp_policy_nz.config.feature_flags import FeatureFlags, _env_bool, load_feature_flags


def test_env_bool_default():
    assert _env_bool("NON_EXISTENT_VAR") is False
    assert _env_bool("NON_EXISTENT_VAR", default=True) is True


def test_env_bool_true_values(monkeypatch):
    for val in ["1", "true", "yes", "on", " TRUE ", "On"]:
        monkeypatch.setenv("TEST_VAR", val)
        assert _env_bool("TEST_VAR") is True


def test_env_bool_false_values(monkeypatch):
    for val in ["0", "false", "no", "off", "anything_else"]:
        monkeypatch.setenv("TEST_VAR", val)
        assert _env_bool("TEST_VAR") is False


def test_feature_flags_default():
    flags = FeatureFlags()
    assert flags.enable_v1 is True
    assert flags.enable_v2 is True
    assert flags.embed_enabled is True
    assert flags.search_enabled is True
    assert flags.process_enabled is True
    assert flags.degraded_embeddings is False
    assert flags.kill_switch is False


def test_feature_flags_is_enabled():
    flags = FeatureFlags()
    assert flags.is_enabled("embed") is True
    assert flags.is_enabled("search") is True
    assert flags.is_enabled("process") is True


def test_feature_flags_kill_switch():
    flags = FeatureFlags(kill_switch=True)
    assert flags.is_enabled("embed") is False
    assert flags.is_enabled("search") is False
    assert flags.is_enabled("process") is False


def test_feature_flags_missing_attr():
    flags = FeatureFlags()
    assert flags.is_enabled("non_existent") is True  # getattr with default=True


def test_load_feature_flags(monkeypatch):
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_V1", "false")
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_V2", "false")
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_EMBED", "0")
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_SEARCH", "no")
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_PROCESS", "off")
    monkeypatch.setenv("NLP_POLICY_NZ_DEGRADED_EMBEDDINGS", "true")
    monkeypatch.setenv("NLP_POLICY_NZ_KILL_SWITCH", "1")

    flags = load_feature_flags()
    assert flags.enable_v1 is False
    assert flags.enable_v2 is False
    assert flags.embed_enabled is False
    assert flags.search_enabled is False
    assert flags.process_enabled is False
    assert flags.degraded_embeddings is True
    assert flags.kill_switch is True
