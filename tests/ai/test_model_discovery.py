"""Tests for model discovery and capability probing."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.control_plane.config import AIConfig
from tools.ai.control_plane.model_discovery import discover_models, fingerprint_models
from tools.ai.control_plane.capability_probe import probe_model
from tools.ai.schemas.models import CallStatus


class TestModelDiscovery:
    def test_discover_unconfigured_returns_empty(self):
        cfg = AIConfig(endpoint="", api_key_present=False)
        models = discover_models(cfg)
        assert models == []

    def test_discover_handles_connection_error(self):
        cfg = AIConfig(endpoint="https://nonexistent.invalid/v1", api_key_present=True)
        with patch("tools.ai.control_plane.config.get_api_key", return_value="test"):
            models = discover_models(cfg)
        assert models == []

    def test_discover_parses_model_list(self):
        cfg = AIConfig(endpoint="https://llm.example.com/v1", api_key_present=True)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "gpt-oss-v1", "context_length": 8192},
                {"id": "embed-v1", "context_length": 512},
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("tools.ai.control_plane.config.get_api_key", return_value="test"):
            with patch("httpx.Client") as mock_client_cls:
                mock_client = MagicMock()
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client.get.return_value = mock_response
                mock_client_cls.return_value = mock_client

                models = discover_models(cfg)

        assert len(models) == 2
        assert models[0].model_id == "gpt-oss-v1"
        assert models[1].supports_embedding is True

    def test_fingerprint_models(self):
        from tools.ai.schemas.models import ModelCapability
        models = [ModelCapability(model_id="test-model")]
        fps = fingerprint_models(models)
        assert len(fps) == 1
        assert len(fps[0].fingerprint_hash) == 16


class TestCapabilityProbe:
    def test_probe_blocked_missing_env(self):
        cfg = AIConfig(endpoint="", api_key_present=False)
        success, text, record = probe_model(cfg, "test-model")
        assert success is False
        assert record.status == CallStatus.blocked_missing_env
