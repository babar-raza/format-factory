"""Tests for gateway.py timeout hardening (GW-001 … GW-005).

All tests use mocked litellm — no live network required.
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))


def _make_ai_config(configured: bool = True):
    """Build a minimal AIConfig-like object."""
    cfg = MagicMock()
    cfg.is_configured = configured
    cfg.endpoint = "http://test-endpoint/v1"
    cfg.endpoint_identity = "test-endpoint"
    cfg.provider_name = "openai"
    return cfg


def _fake_litellm_success(content: str = "grading ok") -> types.ModuleType:
    """Build a fake litellm module that returns a successful response."""
    litellm = types.ModuleType("litellm")
    litellm.suppress_debug_info = False

    mock_response = MagicMock()
    mock_response.choices[0].message.content = content
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15
    litellm.completion = MagicMock(return_value=mock_response)
    return litellm


def _call_gateway(config, litellm_module, env_overrides=None):
    """Call gateway_chat() with a mocked litellm."""
    from tools.ai.schemas.models import AIUsageRecord, CallStatus
    from tools.ai.control_plane.config import AIConfig

    with patch.dict(sys.modules, {"litellm": litellm_module}):
        with patch("tools.ai.control_plane.gateway._get_litellm", return_value=litellm_module):
            with patch("tools.ai.control_plane.config.get_api_key", return_value="fake-key"):
                env = {"GPT_OSS_API_KEY": "fake-key", "GPT_OSS_ENDPOINT": config.endpoint}
                if env_overrides:
                    env.update(env_overrides)
                with patch.dict(os.environ, env):
                    from tools.ai.control_plane.gateway import gateway_chat
                    return gateway_chat(
                        config=config,
                        model="recommended",
                        messages=[{"role": "user", "content": "test"}],
                        role="evidence_review",
                        operation="test_op",
                    )


class TestGatewayTimeout:
    """GW-001 … GW-005: gateway_chat() timeout behaviour."""

    def test_gw001_timeout_passed_to_litellm(self):
        """GW-001: gateway_chat() passes timeout= to litellm.completion()."""
        cfg = _make_ai_config()
        litellm = _fake_litellm_success()

        _call_gateway(cfg, litellm)

        create_calls = litellm.completion.call_args_list
        assert len(create_calls) == 1
        kwargs = create_calls[0].kwargs
        assert "timeout" in kwargs, "timeout= must be passed to litellm.completion()"
        assert kwargs["timeout"] > 0, f"timeout must be positive, got {kwargs['timeout']}"

    def test_gw002_exception_returns_error_record(self):
        """GW-002: litellm raises Exception → response empty, record status=error."""
        cfg = _make_ai_config()
        litellm = types.ModuleType("litellm")
        litellm.suppress_debug_info = False
        litellm.completion = MagicMock(side_effect=Exception("network failure"))

        resp, record = _call_gateway(cfg, litellm)

        assert resp.get("content", "") == ""
        assert str(record.status).lower() in ("error", "callstatus.error")

    def test_gw003_timeout_exception_produces_error_record(self):
        """GW-003: litellm timeout → error_class_redacted set, status=error."""

        class FakeReadTimeout(Exception):
            pass

        cfg = _make_ai_config()
        litellm = types.ModuleType("litellm")
        litellm.suppress_debug_info = False
        litellm.completion = MagicMock(side_effect=FakeReadTimeout("read timed out"))

        resp, record = _call_gateway(cfg, litellm)

        assert resp.get("content", "") == ""
        # error_class_redacted must be set (not None or empty)
        assert record.error_class_redacted, (
            "error_class_redacted must be set when litellm raises a timeout"
        )
        # Should be classified as READ_TIMEOUT by grader_reliability
        assert "READ_TIMEOUT" in record.error_class_redacted or "FakeReadTimeout" in record.error_class_redacted

    def test_gw004_missing_api_key_blocked(self):
        """GW-004: Missing API key → status=blocked_missing_env (regression guard)."""
        cfg = _make_ai_config()
        litellm = _fake_litellm_success()

        with patch.dict(sys.modules, {"litellm": litellm}):
            with patch("tools.ai.control_plane.gateway._get_litellm", return_value=litellm):
                with patch("tools.ai.control_plane.config.get_api_key", return_value=None):
                    with patch.dict(os.environ, {}, clear=True):
                        from tools.ai.control_plane.gateway import gateway_chat
                        resp, record = gateway_chat(
                            config=cfg,
                            model="recommended",
                            messages=[{"role": "user", "content": "test"}],
                        )

        assert resp.get("content", "") == ""
        assert str(record.status).lower() in ("blocked_missing_env", "callstatus.blocked_missing_env")

    def test_gw005_env_override_respected(self):
        """GW-005: GRADER_LLM_TIMEOUT env override changes the timeout passed to litellm."""
        cfg = _make_ai_config()
        litellm = _fake_litellm_success()

        captured_kwargs = {}

        def capture_completion(**kwargs):
            captured_kwargs.update(kwargs)
            resp = MagicMock()
            resp.choices[0].message.content = "ok"
            resp.usage = None
            return resp

        litellm.completion = MagicMock(side_effect=capture_completion)

        _call_gateway(cfg, litellm, env_overrides={"GRADER_LLM_TIMEOUT": "45"})

        assert "timeout" in captured_kwargs
        assert captured_kwargs["timeout"] == 45.0, (
            f"GRADER_LLM_TIMEOUT=45 should produce timeout=45.0, got {captured_kwargs['timeout']}"
        )
