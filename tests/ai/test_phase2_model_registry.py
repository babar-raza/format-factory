"""Tests for Phase 2 model registry enhancements — Lane B."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.control_plane.config import AIConfig
from tools.ai.control_plane.model_discovery import (
    discover_models,
    guess_model_family,
    infer_role_candidates,
)
from tools.ai.control_plane.model_router import ModelRouter
from tools.ai.schemas.models import AIRole, ModelCapability, ModelSelectionRequest


class TestModelFamilyGuess:
    def test_gpt_family(self):
        assert guess_model_family("gpt-4o-mini") == "gpt"

    def test_qwen_family(self):
        assert guess_model_family("qwen2-72b") == "qwen"

    def test_embedding_family(self):
        assert guess_model_family("text-embedding-ada-002") == "embedding"

    def test_llama_family(self):
        assert guess_model_family("llama-3.1-70b") == "llama"

    def test_mistral_family(self):
        assert guess_model_family("mistral-7b") == "mistral"

    def test_unknown_family(self):
        assert guess_model_family("custom-model-v1") == "unknown"

    def test_case_insensitive(self):
        assert guess_model_family("GPT-OSS-V1") == "gpt"


class TestRoleCandidates:
    def test_gpt_candidates(self):
        roles = infer_role_candidates("gpt-oss-v1")
        assert AIRole.structured_extraction in roles

    def test_qwen_candidates(self):
        roles = infer_role_candidates("qwen2-72b")
        assert AIRole.agentic_low_risk in roles

    def test_embedding_candidates(self):
        roles = infer_role_candidates("text-embed-v1")
        assert AIRole.embedding_retrieval in roles


class TestModelCapabilityFields:
    def test_new_fields_default_values(self):
        mc = ModelCapability(model_id="test-model")
        assert mc.supports_json_or_structured_output is False
        assert mc.model_family_guess == ""
        assert mc.role_candidates == []
        assert mc.last_probe_status == ""
        assert mc.endpoint_identity_hash == ""

    def test_new_fields_can_be_set(self):
        mc = ModelCapability(
            model_id="gpt-oss-v1",
            model_family_guess="gpt",
            role_candidates=[AIRole.structured_extraction],
            last_probe_status="success",
            endpoint_identity_hash="abc123",
            supports_json_or_structured_output=True,
        )
        assert mc.model_family_guess == "gpt"
        assert mc.supports_json_or_structured_output is True
        assert mc.endpoint_identity_hash == "abc123"


class TestDiscoverModelsPhase2:
    def test_discover_populates_family_and_candidates(self):
        cfg = AIConfig(endpoint="https://llm.example.com/v1", api_key_present=True)
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"id": "gpt-oss-v1", "context_length": 8192}]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("tools.ai.control_plane.model_discovery.get_api_key", return_value="test"):
            with patch("httpx.Client") as mock_client_cls:
                mock_client = MagicMock()
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_client.get.return_value = mock_response
                mock_client_cls.return_value = mock_client
                models = discover_models(cfg)

        assert len(models) == 1
        assert models[0].model_family_guess == "gpt"
        assert AIRole.structured_extraction in models[0].role_candidates
        assert len(models[0].endpoint_identity_hash) == 12


class TestModelDisappearanceAndReplacement:
    def test_model_disappearance_fails_closed(self):
        models = [
            ModelCapability(model_id="m1", roles=[AIRole.structured_extraction]),
        ]
        router = ModelRouter(models)
        dec = router.select(ModelSelectionRequest(role=AIRole.structured_extraction))
        assert dec.selected_model_id == "m1"

        # Model disappears
        router.update_models([])
        dec = router.select(ModelSelectionRequest(role=AIRole.structured_extraction))
        assert dec.fail_closed is True

    def test_model_replacement_selects_new(self):
        router = ModelRouter([
            ModelCapability(model_id="old-model", roles=[AIRole.summarization]),
        ])
        dec = router.select(ModelSelectionRequest(role=AIRole.summarization))
        assert dec.selected_model_id == "old-model"

        # Replace with new model
        router.update_models([
            ModelCapability(model_id="new-model", roles=[AIRole.summarization]),
        ])
        dec = router.select(ModelSelectionRequest(role=AIRole.summarization))
        assert dec.selected_model_id == "new-model"

    def test_role_mismatch_fails_closed_no_fallback(self):
        # Only embedding model available, but chat role requested
        models = [
            ModelCapability(
                model_id="embed-only",
                supports_chat=False,
                supports_embedding=True,
                roles=[AIRole.embedding_retrieval],
            ),
        ]
        router = ModelRouter(models)
        dec = router.select(ModelSelectionRequest(role=AIRole.structured_extraction))
        # No chat-capable model, so should fail closed
        assert dec.fail_closed is True

    def test_fallback_logging_includes_model_id(self):
        models = [ModelCapability(model_id="generic-chat")]
        router = ModelRouter(models)
        # security_analysis is a no-fallback role — must fail closed
        dec = router.select(ModelSelectionRequest(role=AIRole.security_analysis))
        assert dec.fail_closed is True
        assert dec.fallback_used is False
        # summarization still allows fallback
        dec2 = router.select(ModelSelectionRequest(role=AIRole.summarization))
        assert dec2.fallback_used is True
        assert dec2.fallback_model_id == "generic-chat"
