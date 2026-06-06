"""
Format Factory — Session Skill Backend (Classification Stub)
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001

Classifies SESSION_SKILL_TOOL availability. Honest classification only.

SESSION_SKILL_TOOL is the Skill tool available in a Claude Code session.
It is DISTINCT from:
  - SUPERPOWERS_LOCAL_PLUGIN (not installed)
  - REPO_CLAUDE_COMMAND (via .claude/commands/ — not present)
  - Superpowers plugin

H5 proof via SESSION_SKILL_TOOL requires:
  - Runner dispatches action to this backend
  - Skill tool call returns execution evidence
  - Result file written by runner with backend_used=SESSION_SKILL_TOOL

This sprint: SESSION_SKILL_TOOL is not callable programmatically from runner
(the runner runs in a subprocess; Skill tool is Claude Code session-level API).
Classified as NOT_PROGRAMMATICALLY_INVOCABLE_FROM_RUNNER.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend
)


class SessionSkillBackend(ExecutionBackend):
    """Session Skill Tool backend — honest classification."""

    @property
    def backend_type(self) -> BackendType:
        # Use LLM_API as nearest available type; no SESSION_SKILL_TOOL enum value
        return BackendType.LLM_API

    @property
    def backend_name(self) -> str:
        return "SESSION_SKILL_TOOL"

    def discover(self) -> BackendStatus:
        # Skill tool is session-level API — not discoverable from subprocess
        # Cannot be invoked from next_action_runner subprocess
        return BackendStatus.NOT_FOUND  # Not callable from runner subprocess

    def can_execute(self, action: dict) -> bool:
        return False  # Not programmatically invocable from runner

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        return BackendResult(
            action_id=action.get("action_id", "unknown"),
            backend_used=BackendType.LLM_API,
            status="BLOCKED",
            exit_code=3,
            errors=[
                "SESSION_SKILL_TOOL is not programmatically invocable from next_action_runner subprocess. "
                "H5 via SESSION_SKILL_TOOL requires Claude Code session-level Skill tool invocation "
                "with runner dispatch evidence — not achievable from runner subprocess."
            ],
            warnings=[
                "SESSION_SKILL_TOOL != SUPERPOWERS_LOCAL_PLUGIN. "
                "Proof requires Skill tool call evidence returned to runner, not just Claude Code session."
            ],
        )
