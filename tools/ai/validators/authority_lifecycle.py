"""Artifact authority lifecycle validator.

Enforces the 12-state machine. No skip from ai_draft to authoritative_after_gate.
Provides state record writer/reader and transition evidence tracking.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.ai.schemas.models import (
    ArtifactAuthorityState,
    ArtifactAuthorityStateValue,
    VALID_TRANSITIONS,
)

TERMINAL_STATES = {
    ArtifactAuthorityStateValue.rejected,
    ArtifactAuthorityStateValue.superseded,
}


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


def is_terminal(state: ArtifactAuthorityStateValue) -> bool:
    """Check if a state is terminal (no further transitions allowed)."""
    return state in TERMINAL_STATES


def transition_with_evidence(
    artifact: ArtifactAuthorityState,
    new_state: ArtifactAuthorityStateValue,
    evidence_path: str,
    reason: str = "",
) -> tuple[bool, str]:
    """Attempt a state transition with required evidence path.

    Returns (success, error_message).
    """
    if not evidence_path:
        return False, "transition requires evidence_path"
    if is_terminal(artifact.current_state):
        return False, f"cannot transition from terminal state {artifact.current_state.value}"
    if not can_transition(artifact.current_state, new_state):
        return False, f"invalid transition: {artifact.current_state.value} -> {new_state.value}"

    artifact.transitions.append({
        "from": artifact.current_state.value,
        "to": new_state.value,
        "reason": reason,
        "evidence_path": evidence_path,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    artifact.current_state = new_state
    return True, ""


def write_state_record(
    artifact: ArtifactAuthorityState,
    state_file: Path,
) -> None:
    """Append an artifact state record to a JSONL state file."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "artifact_id": artifact.artifact_id,
        "current_state": artifact.current_state.value,
        "transitions": artifact.transitions,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(state_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def read_state_records(state_file: Path) -> list[dict[str, Any]]:
    """Read all state records from a JSONL state file."""
    if not state_file.exists():
        return []
    records: list[dict[str, Any]] = []
    with open(state_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def count_by_state(state_file: Path) -> dict[str, int]:
    """Count artifacts by their current state."""
    records = read_state_records(state_file)
    counts: dict[str, int] = {}
    for rec in records:
        state = rec.get("current_state", "unknown")
        counts[state] = counts.get(state, 0) + 1
    return counts
