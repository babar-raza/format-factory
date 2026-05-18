"""Artifact authority lifecycle validator.

Enforces the 12-state machine. No skip from ai_draft to authoritative_after_gate.
"""

from __future__ import annotations

from tools.ai.schemas.models import (
    ArtifactAuthorityState,
    ArtifactAuthorityStateValue,
    VALID_TRANSITIONS,
)


def can_transition(
    current: ArtifactAuthorityStateValue,
    target: ArtifactAuthorityStateValue,
) -> bool:
    """Check if a state transition is valid without performing it."""
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed


def validate_transition_chain(states: list[ArtifactAuthorityStateValue]) -> list[str]:
    """Validate a sequence of state transitions. Returns list of errors."""
    errors: list[str] = []
    for i in range(len(states) - 1):
        if not can_transition(states[i], states[i + 1]):
            errors.append(
                f"Invalid transition: {states[i].value} -> {states[i + 1].value} (step {i})"
            )
    return errors
