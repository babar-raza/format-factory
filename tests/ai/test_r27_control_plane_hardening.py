"""Lane B tests — control-plane hardening.

Tests for strict fallback policy, role enforcement, and no-fallback roles.
"""

import pytest
from tools.ai.schemas.models import AIRole, ModelCapability, ModelSelectionRequest
from tools.ai.control_plane.model_router import ModelRouter, NO_FALLBACK_ROLES, load_role_requirements


def _make_model(model_id: str, roles: list[AIRole] | None = None, **kwargs) -> ModelCapability:
    return ModelCapability(model_id=model_id, roles=roles or [], **kwargs)


class TestNoFallbackRoles:
    def test_agentic_low_risk_no_fallback(self):
        """agentic_low_risk must fail closed, never fallback."""
        gpt = _make_model("gpt-oss", roles=[AIRole.structured_extraction])
        router = ModelRouter(available_models=[gpt])
        req = ModelSelectionRequest(role=AIRole.agentic_low_risk)
        decision = router.select(req)
        assert decision.fail_closed is True
        assert decision.fallback_used is False

    def test_security_analysis_no_fallback(self):
        """security_analysis must fail closed, never fallback."""
        gpt = _make_model("gpt-oss", roles=[AIRole.structured_extraction])
        router = ModelRouter(available_models=[gpt])
        req = ModelSelectionRequest(role=AIRole.security_analysis)
        decision = router.select(req)
        assert decision.fail_closed is True
        assert decision.fallback_used is False

    def test_summarization_allows_fallback(self):
        """Non-restricted roles can fall back to any chat model."""
        gpt = _make_model("gpt-oss", roles=[AIRole.structured_extraction])
        router = ModelRouter(available_models=[gpt])
        req = ModelSelectionRequest(role=AIRole.summarization)
        decision = router.select(req)
        assert decision.fallback_used is True
        assert decision.fail_closed is False


class TestRoleEnforcement:
    def test_qwen2_restriction_for_agentic(self):
        """agentic_low_risk with qwen2_only restriction should only match qwen models."""
        role_reqs = {"agentic_low_risk": {"restricted_to": "qwen2_only"}}
        gpt = _make_model("gpt-oss", roles=[AIRole.agentic_low_risk])
        qwen = _make_model("qwen3-next", roles=[AIRole.agentic_low_risk])
        router = ModelRouter(available_models=[gpt, qwen], role_requirements=role_reqs)
        req = ModelSelectionRequest(role=AIRole.agentic_low_risk)
        decision = router.select(req)
        assert decision.selected_model_id == "qwen3-next"

    def test_embedding_restriction(self):
        """embedding_retrieval with requires_embedding should only match embedding models."""
        role_reqs = {"embedding_retrieval": {"requires_embedding": True}}
        gpt = _make_model("gpt-oss", roles=[AIRole.embedding_retrieval])
        embed = _make_model("qwen3-embedding-8b", roles=[AIRole.embedding_retrieval], supports_embedding=True)
        router = ModelRouter(available_models=[gpt, embed], role_requirements=role_reqs)
        req = ModelSelectionRequest(role=AIRole.embedding_retrieval)
        decision = router.select(req)
        assert decision.selected_model_id == "qwen3-embedding-8b"


class TestNoModelAvailable:
    def test_completely_empty_models(self):
        """No models at all should fail closed."""
        router = ModelRouter(available_models=[])
        req = ModelSelectionRequest(role=AIRole.structured_extraction)
        decision = router.select(req)
        assert decision.fail_closed is True

    def test_role_mismatch_all_models(self):
        """Models exist but none match the requested role — restricted roles fail closed."""
        gpt = _make_model("gpt-oss", roles=[AIRole.summarization])
        router = ModelRouter(available_models=[gpt])
        req = ModelSelectionRequest(role=AIRole.agentic_low_risk)
        decision = router.select(req)
        assert decision.fail_closed is True


class TestLoadRoleRequirements:
    def test_load_from_contracts(self, tmp_path):
        import yaml
        roles_yaml = {
            "roles": {
                "agentic_low_risk": {"restricted_to": "qwen2_only", "requires_chat": True},
                "embedding_retrieval": {"requires_embedding": True},
            }
        }
        roles_file = tmp_path / "roles.yaml"
        with open(roles_file, "w") as f:
            yaml.dump(roles_yaml, f)
        reqs = load_role_requirements(tmp_path)
        assert "agentic_low_risk" in reqs
        assert reqs["agentic_low_risk"]["restricted_to"] == "qwen2_only"

    def test_missing_contracts_dir(self, tmp_path):
        reqs = load_role_requirements(tmp_path / "nonexistent")
        assert reqs == {}
