"""agent.config — 키 유무에 따른 모델 선택을 검증한다."""

import pytest

from agent import config


def test_no_keys_means_no_models(monkeypatch):
    for env_var, _model in config.PROVIDERS:
        monkeypatch.delenv(env_var, raising=False)
    assert config.available_models() == []


def test_pick_model_without_keys_exits_with_guidance(monkeypatch):
    for env_var, _model in config.PROVIDERS:
        monkeypatch.delenv(env_var, raising=False)
    with pytest.raises(SystemExit) as exc:
        config.pick_model()
    assert ".env" in str(exc.value)  # 안내문이 해결 방법을 담는다


def test_priority_follows_provider_order(monkeypatch):
    # 셋 다 채우면 첫 번째(Google)가 뽑힌다
    for env_var, _model in config.PROVIDERS:
        monkeypatch.setenv(env_var, "test-key")
    assert config.pick_model() == config.PROVIDERS[0][1]


def test_single_key_wins_regardless_of_position(monkeypatch):
    for env_var, _model in config.PROVIDERS:
        monkeypatch.delenv(env_var, raising=False)
    last_env, last_model = config.PROVIDERS[-1]
    monkeypatch.setenv(last_env, "test-key")
    assert config.pick_model() == last_model
