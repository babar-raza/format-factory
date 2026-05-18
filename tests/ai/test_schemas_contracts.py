"""Tests for AI Platform Pydantic schemas and YAML contracts."""

import os
import sys
from pathlib import Path

import pytest
import yaml

# Ensure tools/ is importable
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from pydantic import ValidationError

from tools.ai.schemas.models import (
    AIProviderConfig,
    AIRole,
    AITaskContract,
    AIUsageRecord,
    ArtifactAuthorityState,
    ArtifactAuthorityStateValue,
    CallStatus,
    ModelCapability,
    ModelFingerprint,
    ModelSelectionDecision,
    ModelSelectionRequest,
    PromptTemplateRecord,
    RuntimeGuardResult,
    ValidationResult,
)
from tools.ai.prompts.registry import get_template, PROBE_TEMPLATES


# --- Schema validation: valid data ---

class TestSchemasValidData:
    def test_provider_config_valid(self):
        cfg = AIProviderConfig(endpoint="https://llm.professionalize.com/v1")
        assert cfg.endpoint == "https://llm.professionalize.com/v1"
        assert cfg.api_key_env_var == "GPT_OSS_API_KEY"

    def test_model_capability(self):
        mc = ModelCapability(model_id="gpt-oss-v1", roles=[AIRole.structured_extraction])
        assert mc.supports_chat is True
        assert AIRole.structured_extraction in mc.roles

    def test_model_fingerprint_hash(self):
        fp = ModelFingerprint(model_id="gpt-oss-v1", provider="openai")
        h = fp.compute_hash()
        assert len(h) == 16
        assert fp.fingerprint_hash == h

    def test_model_selection_request(self):
        req = ModelSelectionRequest(role=AIRole.test_generation)
        assert req.role == AIRole.test_generation

    def test_model_selection_decision_fail_closed(self):
        dec = ModelSelectionDecision(
            role=AIRole.security_analysis,
            fail_closed=True,
            reason="No model available for role",
        )
        assert dec.fail_closed is True
        assert dec.selected_model_id is None

    def test_task_contract(self):
        tc = AITaskContract(
            task_id="test-001",
            task_type="capability_probe",
            role=AIRole.structured_extraction,
        )
        assert tc.max_retries == 1
        assert tc.timeout_seconds == 30

    def test_prompt_template_hash(self):
        pt = PromptTemplateRecord(
            template_id="test",
            template_text="Hello world",
        )
        h = pt.compute_hash()
        assert len(h) == 16

    def test_usage_record(self):
        rec = AIUsageRecord(
            provider="openai",
            model="gpt-oss-v1",
            role="structured_extraction",
            operation="capability_probe",
            status=CallStatus.success,
        )
        assert rec.posted_to_agent_metrics is False
        assert rec.api_calls_count == 1

    def test_artifact_authority_state(self):
        art = ArtifactAuthorityState(artifact_id="test-artifact")
        assert art.current_state == ArtifactAuthorityStateValue.ai_draft

    def test_validation_result(self):
        vr = ValidationResult(valid=True)
        assert vr.errors == []

    def test_runtime_guard_result(self):
        rg = RuntimeGuardResult(passed=True, scanned_paths=["src/python/"])
        assert rg.violations == []


# --- Schema validation: invalid data ---

class TestSchemasInvalidData:
    def test_provider_config_secret_in_url(self):
        with pytest.raises(ValidationError, match="secret"):
            AIProviderConfig(endpoint="https://example.com?key=abc123")

    def test_task_contract_retries_too_high(self):
        with pytest.raises(ValidationError):
            AITaskContract(
                task_id="x",
                task_type="x",
                role=AIRole.summarization,
                max_retries=10,
            )

    def test_task_contract_timeout_too_low(self):
        with pytest.raises(ValidationError):
            AITaskContract(
                task_id="x",
                task_type="x",
                role=AIRole.summarization,
                timeout_seconds=0,
            )

    def test_invalid_role(self):
        with pytest.raises(ValueError):
            AIRole("nonexistent_role")


# --- Authority lifecycle ---

class TestAuthorityLifecycle:
    def test_valid_forward_transition(self):
        art = ArtifactAuthorityState(artifact_id="t1")
        assert art.transition_to(ArtifactAuthorityStateValue.schema_validated) is True
        assert art.current_state == ArtifactAuthorityStateValue.schema_validated

    def test_invalid_skip_transition(self):
        art = ArtifactAuthorityState(artifact_id="t2")
        assert art.transition_to(ArtifactAuthorityStateValue.authoritative_after_gate) is False
        assert art.current_state == ArtifactAuthorityStateValue.ai_draft

    def test_rejection_from_any_non_terminal(self):
        art = ArtifactAuthorityState(artifact_id="t3")
        art.transition_to(ArtifactAuthorityStateValue.schema_validated)
        assert art.transition_to(ArtifactAuthorityStateValue.rejected) is True

    def test_no_transition_from_terminal(self):
        art = ArtifactAuthorityState(artifact_id="t4")
        art.transition_to(ArtifactAuthorityStateValue.rejected)
        assert art.transition_to(ArtifactAuthorityStateValue.ai_draft) is False


# --- YAML contracts ---

class TestYAMLContracts:
    CONTRACTS_DIR = REPO_ROOT / "tools" / "ai" / "contracts"

    def test_roles_yaml_loads(self):
        with open(self.CONTRACTS_DIR / "roles.yaml") as f:
            data = yaml.safe_load(f)
        assert "roles" in data
        assert "structured_extraction" in data["roles"]

    def test_task_types_yaml_loads(self):
        with open(self.CONTRACTS_DIR / "task-types.yaml") as f:
            data = yaml.safe_load(f)
        assert "task_types" in data

    def test_artifact_authority_states_yaml_loads(self):
        with open(self.CONTRACTS_DIR / "artifact-authority-states.yaml") as f:
            data = yaml.safe_load(f)
        assert "states" in data
        assert len(data["states"]) == 12

    def test_forbidden_runtime_imports_yaml_loads(self):
        with open(self.CONTRACTS_DIR / "forbidden-runtime-imports.yaml") as f:
            data = yaml.safe_load(f)
        assert "forbidden_imports" in data
        assert "litellm" in data["forbidden_imports"]

    def test_telemetry_schema_yaml_loads(self):
        with open(self.CONTRACTS_DIR / "telemetry-schema.yaml") as f:
            data = yaml.safe_load(f)
        assert "record_fields" in data


# --- Prompt registry ---

class TestPromptRegistry:
    def test_probe_templates_registered(self):
        assert "capability_probe_v1" in PROBE_TEMPLATES
        assert "model_identity_probe_v1" in PROBE_TEMPLATES

    def test_template_has_hash(self):
        t = get_template("capability_probe_v1")
        assert t is not None
        assert len(t.prompt_hash) == 16

    def test_get_nonexistent_template(self):
        assert get_template("nonexistent") is None
