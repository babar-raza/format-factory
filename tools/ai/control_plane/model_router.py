"""Role-based model router — selects models by role, not by hardcoded name.

Fails closed if no model satisfies a role.
Records fallback decisions.
"""

from __future__ import annotations

from tools.ai.schemas.models import (
    AIRole,
    ModelCapability,
    ModelSelectionDecision,
    ModelSelectionRequest,
)


class ModelRouter:
    """Routes model selection requests to available models by role."""

    def __init__(self, available_models: list[ModelCapability] | None = None):
        self._models: list[ModelCapability] = available_models or []

    def update_models(self, models: list[ModelCapability]) -> None:
        self._models = list(models)

    def select(self, request: ModelSelectionRequest) -> ModelSelectionDecision:
        """Select a model for the requested role.

        Returns a decision with fail_closed=True if no model satisfies the role.
        """
        # Find models assigned to this role
        candidates = [m for m in self._models if request.role in m.roles]

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
