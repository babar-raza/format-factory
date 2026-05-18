"""Pydantic v2 models for AI Platform Phase 1 control plane."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# --- Enums ---

class AIRole(str, Enum):
    """Roles for model routing. Models are assigned to roles, not hardcoded."""
    structured_extraction = "structured_extraction"
    security_analysis = "security_analysis"
    test_generation = "test_generation"
    evidence_review = "evidence_review"
    summarization = "summarization"
    embedding_retrieval = "embedding_retrieval"
    agentic_low_risk = "agentic_low_risk"


class ArtifactAuthorityStateValue(str, Enum):
    """12-state artifact authority lifecycle."""
    ai_draft = "ai_draft"
    schema_validated = "schema_validated"
    source_cited = "source_cited"
    source_verified = "source_verified"
    contradiction_checked = "contradiction_checked"
    evaluator_passed = "evaluator_passed"
    accepted_for_planning = "accepted_for_planning"
    accepted_for_tests = "accepted_for_tests"
    accepted_for_source_requirements = "accepted_for_source_requirements"
    authoritative_after_gate = "authoritative_after_gate"
    rejected = "rejected"
    superseded = "superseded"


class CallStatus(str, Enum):
    success = "success"
    error = "error"
    blocked_missing_env = "blocked_missing_env"
    blocked_no_model = "blocked_no_model"
    blocked_fail_closed = "blocked_fail_closed"


# --- Provider and Model schemas ---

class AIProviderConfig(BaseModel):
    """Configuration for an AI provider endpoint. Loaded from env vars."""
    endpoint: str = Field(description="Base URL for the AI endpoint")
    api_key_env_var: str = Field(
        default="GPT_OSS_API_KEY",
        description="Name of the env var holding the API key (never the value)"
    )
    endpoint_env_var: str = Field(
        default="GPT_OSS_ENDPOINT",
        description="Name of the env var holding the endpoint URL"
    )
    provider_name: str = Field(default="openai", description="LiteLLM provider name")

    @field_validator("endpoint")
    @classmethod
    def endpoint_no_secret(cls, v: str) -> str:
        if "key=" in v.lower() or "token=" in v.lower():
            raise ValueError("Endpoint URL must not contain embedded secrets")
        return v


class ModelCapability(BaseModel):
    """A discovered model and its capabilities."""
    model_id: str
    provider: str = "openai"
    supports_chat: bool = True
    supports_completion: bool = False
    supports_embedding: bool = False
    context_length: Optional[int] = None
    roles: list[AIRole] = Field(default_factory=list)


class ModelFingerprint(BaseModel):
    """Fingerprint for a model at discovery time."""
    model_id: str
    provider: str
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    fingerprint_hash: str = ""

    def compute_hash(self) -> str:
        raw = f"{self.model_id}|{self.provider}|{self.discovered_at.isoformat()}"
        self.fingerprint_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self.fingerprint_hash


# --- Routing schemas ---

class ModelSelectionRequest(BaseModel):
    """Request for model routing by role."""
    role: AIRole
    task_type: str = ""
    prefer_model_id: Optional[str] = None


class ModelSelectionDecision(BaseModel):
    """Decision from the model router."""
    role: AIRole
    selected_model_id: Optional[str] = None
    fallback_used: bool = False
    fallback_model_id: Optional[str] = None
    fail_closed: bool = False
    reason: str = ""


# --- Task and prompt schemas ---

class AITaskContract(BaseModel):
    """Contract defining an AI task's constraints."""
    task_id: str
    task_type: str
    role: AIRole
    allowed_operations: list[str] = Field(default_factory=list)
    forbidden_operations: list[str] = Field(default_factory=list)
    max_retries: int = Field(default=1, ge=0, le=5)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    require_citation: bool = False
    require_contradiction_check: bool = False


class PromptTemplateRecord(BaseModel):
    """Registry entry for a prompt template."""
    template_id: str
    version: str = "1.0.0"
    template_text: str
    prompt_hash: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_hash(self) -> str:
        self.prompt_hash = hashlib.sha256(self.template_text.encode()).hexdigest()[:16]
        return self.prompt_hash


# --- Telemetry schema ---

class AIUsageRecord(BaseModel):
    """Telemetry record for a single AI gateway call."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: str = ""
    sprint_id: str = ""
    taskcard_id: str = ""
    gate_id: str = ""
    provider: str = ""
    endpoint_identity: str = Field(
        default="",
        description="Endpoint identity without secret (e.g. hostname only)"
    )
    model: str = ""
    role: str = ""
    operation: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    api_calls_count: int = 1
    status: CallStatus = CallStatus.success
    error_class_redacted: str = ""
    prompt_hash: str = ""
    input_artifact_hashes: list[str] = Field(default_factory=list)
    output_artifact_hashes: list[str] = Field(default_factory=list)
    model_fingerprint: str = ""
    fallback_used: bool = False
    evidence_path: str = ""
    posted_to_agent_metrics: bool = False


# --- Validation schemas ---

class ArtifactAuthorityState(BaseModel):
    """Tracks authority state of an AI-produced artifact."""
    artifact_id: str
    current_state: ArtifactAuthorityStateValue = ArtifactAuthorityStateValue.ai_draft
    transitions: list[dict[str, Any]] = Field(default_factory=list)

    def transition_to(self, new_state: ArtifactAuthorityStateValue, reason: str = "") -> bool:
        """Attempt a state transition. Returns True if valid, False if blocked."""
        allowed = VALID_TRANSITIONS.get(self.current_state, set())
        if new_state not in allowed:
            return False
        self.transitions.append({
            "from": self.current_state.value,
            "to": new_state.value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self.current_state = new_state
        return True


class ValidationResult(BaseModel):
    """Result of a schema or content validation."""
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeGuardResult(BaseModel):
    """Result of a runtime AI-import guard scan."""
    scanned_paths: list[str] = Field(default_factory=list)
    violations: list[dict[str, str]] = Field(default_factory=list)
    passed: bool = True
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Authority lifecycle valid transitions ---

VALID_TRANSITIONS: dict[ArtifactAuthorityStateValue, set[ArtifactAuthorityStateValue]] = {
    ArtifactAuthorityStateValue.ai_draft: {
        ArtifactAuthorityStateValue.schema_validated,
        ArtifactAuthorityStateValue.rejected,
    },
    ArtifactAuthorityStateValue.schema_validated: {
        ArtifactAuthorityStateValue.source_cited,
        ArtifactAuthorityStateValue.rejected,
    },
    ArtifactAuthorityStateValue.source_cited: {
        ArtifactAuthorityStateValue.source_verified,
        ArtifactAuthorityStateValue.rejected,
    },
    ArtifactAuthorityStateValue.source_verified: {
        ArtifactAuthorityStateValue.contradiction_checked,
        ArtifactAuthorityStateValue.rejected,
    },
    ArtifactAuthorityStateValue.contradiction_checked: {
        ArtifactAuthorityStateValue.evaluator_passed,
        ArtifactAuthorityStateValue.rejected,
    },
    ArtifactAuthorityStateValue.evaluator_passed: {
        ArtifactAuthorityStateValue.accepted_for_planning,
        ArtifactAuthorityStateValue.rejected,
    },
    ArtifactAuthorityStateValue.accepted_for_planning: {
        ArtifactAuthorityStateValue.accepted_for_tests,
        ArtifactAuthorityStateValue.rejected,
        ArtifactAuthorityStateValue.superseded,
    },
    ArtifactAuthorityStateValue.accepted_for_tests: {
        ArtifactAuthorityStateValue.accepted_for_source_requirements,
        ArtifactAuthorityStateValue.rejected,
        ArtifactAuthorityStateValue.superseded,
    },
    ArtifactAuthorityStateValue.accepted_for_source_requirements: {
        ArtifactAuthorityStateValue.authoritative_after_gate,
        ArtifactAuthorityStateValue.rejected,
        ArtifactAuthorityStateValue.superseded,
    },
    ArtifactAuthorityStateValue.authoritative_after_gate: {
        ArtifactAuthorityStateValue.superseded,
    },
    ArtifactAuthorityStateValue.rejected: set(),
    ArtifactAuthorityStateValue.superseded: set(),
}
