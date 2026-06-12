"""Tests for role-based model router."""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.control_plane.model_router import ModelRouter
from tools.ai.schemas.models import AIRole, ModelCapability, ModelSelectionRequest


class TestModelRouter:
    def test_select_by_role(self):
        models = [
            ModelCapability(model_id="m1", roles=[AIRole.structured_extraction]),
            ModelCapability(model_id="m2", roles=[AIRole.security_analysis]),
        ]
        router = ModelRouter(models)
        dec = router.select(ModelSelectionRequest(role=AIRole.structured_extraction))
        assert dec.selected_model_id == "m1"
        assert dec.fail_closed is False

    def test_select_preferred_model(self):
        models = [
            ModelCapability(model_id="m1", roles=[AIRole.test_generation]),
            ModelCapability(model_id="m2", roles=[AIRole.test_generation]),
        ]
        router = ModelRouter(models)
        dec = router.select(ModelSelectionRequest(
            role=AIRole.test_generation,
            prefer_model_id="m2",
        ))
        assert dec.selected_model_id == "m2"

    def test_fail_closed_no_models(self):
        router = ModelRouter([])
        dec = router.select(ModelSelectionRequest(role=AIRole.security_analysis))
        assert dec.fail_closed is True
        assert dec.selected_model_id is None

    def test_fallback_to_chat_model(self):
        models = [ModelCapability(model_id="generic", roles=[])]
        router = ModelRouter(models)
        dec = router.select(ModelSelectionRequest(role=AIRole.evidence_review))
        assert dec.fallback_used is True
        assert dec.selected_model_id == "generic"

    def test_update_models(self):
        router = ModelRouter([])
        dec = router.select(ModelSelectionRequest(role=AIRole.summarization))
        assert dec.fail_closed is True

        router.update_models([
            ModelCapability(model_id="new", roles=[AIRole.summarization])
        ])
        dec = router.select(ModelSelectionRequest(role=AIRole.summarization))
        assert dec.selected_model_id == "new"
        assert dec.fail_closed is False

    def test_fallback_logged(self):
        models = [ModelCapability(model_id="fallback-m")]
        router = ModelRouter(models)
        # agentic_low_risk is a no-fallback role — must fail closed
        dec = router.select(ModelSelectionRequest(role=AIRole.agentic_low_risk))
        assert dec.fail_closed is True
        assert dec.fallback_used is False
        # evidence_review still allows fallback
        dec2 = router.select(ModelSelectionRequest(role=AIRole.evidence_review))
        assert dec2.fallback_used is True
        assert dec2.fallback_model_id == "fallback-m"
