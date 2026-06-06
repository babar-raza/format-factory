"""
Format Factory — Skill Seekers Backend (Stub)
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Generated SKILL.md is a candidate only — NOT an installed/callable skill.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend
)


class SkillSeekersBackend(ExecutionBackend):
    """
    Skill Seekers backend — generates skill candidates.
    Generated SKILL.md ≠ installed skill. Proof requires Skill tool invocation evidence.
    """

    @property
    def backend_type(self) -> BackendType:
        return BackendType.REPO_LOCAL_SKILL

    def discover(self) -> BackendStatus:
        try:
            import skill_seekers  # noqa: F401
            return BackendStatus.SETUP_REQUIRED
        except ImportError:
            return BackendStatus.NOT_FOUND

    def can_execute(self, action: dict) -> bool:
        return False  # Generated skill candidate is not callable

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        return BackendResult(
            action_id=action.get("action_id", "unknown"),
            backend_used=BackendType.REPO_LOCAL_SKILL,
            status="BLOCKED",
            exit_code=3,
            errors=[
                "SKILL_SEEKERS_GENERATED_NE_INSTALLED: skill_seekers generates skill candidates. "
                "A generated SKILL.md is NOT an installed/callable skill. "
                "Proof requires Skill tool invocation with execution evidence transcript."
            ],
        )
