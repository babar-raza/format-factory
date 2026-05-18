"""Tests for AI gateway — config, env loading, secret redaction."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.control_plane.config import AIConfig, load_ai_config, get_api_key
from tools.ai.control_plane.gateway import gateway_chat
from tools.ai.schemas.models import CallStatus


class TestConfig:
    def test_load_config_no_env(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = load_ai_config()
            assert cfg.is_configured is False
            assert cfg.endpoint == ""
            assert cfg.api_key_present is False

    def test_load_config_with_env(self):
        env = {
            "GPT_OSS_ENDPOINT": "https://llm.example.com/v1",
            "GPT_OSS_API_KEY": "test-key-123",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_ai_config()
            assert cfg.is_configured is True
            assert cfg.endpoint == "https://llm.example.com/v1"
            assert cfg.api_key_present is True

    def test_endpoint_identity_strips_secrets(self):
        cfg = AIConfig(
            endpoint="https://llm.example.com/v1?token=abc",
            api_key_present=True,
        )
        assert cfg.endpoint_identity == "llm.example.com"
        assert "abc" not in cfg.endpoint_identity

    def test_get_api_key_returns_none_when_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            assert get_api_key() is None

    def test_alias_env_vars(self):
        env = {
            "PROFESSIONALIZE_BASE_URL": "https://alt.example.com/v1",
            "PROFESSIONALIZE_API_KEY": "alt-key",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_ai_config()
            assert cfg.is_configured is True
            assert cfg.endpoint == "https://alt.example.com/v1"


class TestGateway:
    def test_gateway_blocked_missing_env(self):
        cfg = AIConfig(endpoint="", api_key_present=False)
        resp, record = gateway_chat(cfg, model="test", messages=[])
        assert record.status == CallStatus.blocked_missing_env
        assert resp["content"] == ""

    def test_gateway_does_not_print_secrets(self, capsys):
        env = {
            "GPT_OSS_ENDPOINT": "https://llm.example.com/v1",
            "GPT_OSS_API_KEY": "SUPER_SECRET_KEY_12345",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = load_ai_config()
            # Gateway will fail (no real endpoint) but should not print key
            resp, record = gateway_chat(
                cfg,
                model="nonexistent",
                messages=[{"role": "user", "content": "test"}],
            )
            captured = capsys.readouterr()
            assert "SUPER_SECRET_KEY_12345" not in captured.out
            assert "SUPER_SECRET_KEY_12345" not in captured.err
            assert "SUPER_SECRET_KEY_12345" not in str(record.model_dump())
