import os
import pytest


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.test.com")
    monkeypatch.setenv("DEEPSEEK_MODEL", "test-model")
    monkeypatch.setenv("TUSHARE_TOKEN", "test-token")

    from app.config import Settings

    s = Settings()
    assert s.deepseek_api_key == "test-key"
    assert s.deepseek_base_url == "https://api.test.com"
    assert s.deepseek_model == "test-model"
    assert s.tushare_token == "test-token"
    assert s.max_history_rounds == 20


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "k")
    monkeypatch.setenv("TUSHARE_TOKEN", "t")

    from app.config import Settings

    s = Settings()
    assert s.deepseek_base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert s.deepseek_model == "deepseek-v3"
    assert s.max_history_rounds == 20
