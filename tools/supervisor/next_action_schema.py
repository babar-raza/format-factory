"""
Format Factory — Next-Action Schema v2
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Defines the schema and validator for next-action.json files.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


REQUIRED_FIELDS = ["action_id", "action_type", "objective", "preferred_backend"]

FORBIDDEN_ACTION_TYPES = {
    "GIT_PUSH", "GIT_COMMIT", "GIT_RESET", "GIT_STASH", "GIT_CLEAN",
    "GATE_8_APPROVAL", "GATE_11_APPROVAL",
    "PACKAGE_PUBLISH", "PYPI_PUBLISH", "NUGET_PUBLISH",
    "MCP_ACTIVATE", "MCP_DAEMON_START",
    "MODIFY_PRODUCT_SRC",   # src/ changes not allowed in autonomy sprint
    "MUTATE_POC_TARGETS",
}

VALID_ACTION_TYPES = {
    "RUN_JSON_VALIDATION",
    "RUN_YAML_VALIDATION",
    "RUN_MD_NONEMPTY_CHECK",
    "RUN_COMMAND_DISCOVERY",
    "INSPECT_PACKAGE",
    "UPDATE_STATE",
    "GENERATE_EVIDENCE_STUB",
    "RUN_PYTHON_TESTS",
    "RUN_SHELL_COMMAND",
    "SKILL_TOOL_INVOKE",
    "AGENT_SUBAGENT_INVOKE",
    "LLM_API_CALL",
    "MCP_TOOL_CALL",
    "READ_FILE",
    "WRITE_EVIDENCE_FILE",
}


class NextActionValidationError(Exception):
    """Raised when a next-action is invalid."""


def validate_next_action(action: Dict[str, Any]) -> None:
    """
    Validate a next-action dict against schema v2.
    Raises NextActionValidationError on failure.
    """
    # Check required fields
    missing = [f for f in REQUIRED_FIELDS if f not in action]
    if missing:
        raise NextActionValidationError(f"Missing required fields: {missing}")

    # Check action_type is not forbidden
    action_type = action.get("action_type", "")
    if action_type in FORBIDDEN_ACTION_TYPES:
        raise NextActionValidationError(
            f"Forbidden action_type: {action_type}. "
            f"This action cannot be executed autonomously."
        )

    # Warn if action_type is unknown (but allow extensibility)
    # Not hard-error to allow future action types

    # Check forbidden_actions list if present
    forbidden = action.get("forbidden_actions", [])
    if not isinstance(forbidden, list):
        raise NextActionValidationError("forbidden_actions must be a list")

    # Check external_gate is not combined with executable action
    if action.get("external_gate") and action_type not in (None, "", "MANUAL_EXTERNAL_GATE"):
        # external_gate + real action → stop, do not execute
        if action_type != "MANUAL_EXTERNAL_GATE":
            raise NextActionValidationError(
                f"action_type={action_type} combined with external_gate=true. "
                f"This requires human intervention."
            )

    # Validate allowed_write_roots is a list if present
    if "allowed_write_roots" in action:
        if not isinstance(action["allowed_write_roots"], list):
            raise NextActionValidationError("allowed_write_roots must be a list")


def load_and_validate(path: str) -> Dict[str, Any]:
    """Load a next-action JSON file and validate it."""
    p = Path(path)
    if not p.exists():
        raise NextActionValidationError(f"Next-action file not found: {path}")
    try:
        action = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise NextActionValidationError(f"Invalid JSON in {path}: {e}")
    validate_next_action(action)
    return action
