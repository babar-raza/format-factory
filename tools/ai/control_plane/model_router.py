"""Role-based model router — selects models by role, not by hardcoded name.

Fails closed if no model satisfies a role.
Records fallback decisions.
Enforces strict no-fallback for agentic_low_risk and security_analysis.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.ai.schemas.models import (
    AIRole,
    ModelCapability,
    ModelSelectionDecision,
    ModelSelectionRequest,
)

# Roles that must NEVER use fallback — they fail closed without exception
NO_FALLBACK_ROLES: set[AIRole] = {
    AIRole.agentic_low_risk,
    AIRole.security_analysis,
}


def load_role_requirements(contracts_dir: Path | None = None) -> dict[str, dict]:
    """Load role requirements from roles.yaml contract."""
    if contracts_dir is None:
        contracts_dir = Path(__file__).parent.parent / "contracts"
    roles_path = contracts_dir / "roles.yaml"
    if not roles_path.exists():
        return {}
    with open(roles_path) as f:
        data = yaml.safe_load(f)
    return data.get("roles", {})


class ModelRouter:
    """Routes model selection requests to available models by role."""

    def __init__(
        self,
        available_models: list[ModelCapability] | None = None,
        role_requirements: dict[str, dict] | None = None,
    ):
        self._models: list[ModelCapability] = available_models or []
        self._role_reqs: dict[str, dict] = role_requirements or {}

    def update_models(self, models: list[ModelCapability]) -> None:
        self._models = list(models)

    def select(self, request: ModelSelectionRequest) -> ModelSelectionDecision:
        """Select a model for the requested role.

        Returns a decision with fail_closed=True if no model satisfies the role.
        Enforces strict no-fallback for agentic_low_risk and security_analysis.
        """
        role_req = self._role_reqs.get(request.role.value, {})

        # Find models assigned to this role
        candidates = [m for m in self._models if request.role in m.roles]

        # Enforce role-specific requirements from contract
        if role_req.get("requires_embedding"):
            candidates = [m for m in candidates if m.supports_embedding]
        if role_req.get("restricted_to") == "qwen2_only":
            candidates = [m for m in candidates if "qwen" in m.model_id.lower()]

        # Check for preferred model
        if request.prefer_model_id and candidates:
            preferred = [m for m in candidates if m.model_id == request.prefer_model_id]
            if preferred:
                return ModelSelectionDecision(
                    role=request.role,
                    selected_model_id=preferred[0].model_id,
                    reason="preferred_model_available",
                )

        # Select first available candidate
        if candidates:
            return ModelSelectionDecision(
                role=request.role,
                selected_model_id=candidates[0].model_id,
                reason="role_match",
            )

        # NO FALLBACK for restricted roles — fail closed immediately
        if request.role in NO_FALLBACK_ROLES:
            return ModelSelectionDecision(
                role=request.role,
                fail_closed=True,
                reason=f"no_model_for_{request.role.value}_and_fallback_forbidden",
            )

        # Fallback: try any chat-capable model if role has no assigned models
        chat_models = [m for m in self._models if m.supports_chat]
        if chat_models:
            return ModelSelectionDecision(
                role=request.role,
                selected_model_id=chat_models[0].model_id,
                fallback_used=True,
                fallback_model_id=chat_models[0].model_id,
                reason="fallback_no_role_assignment",
            )

        # Fail closed
        return ModelSelectionDecision(
            role=request.role,
            fail_closed=True,
            reason="no_model_available",
        )
