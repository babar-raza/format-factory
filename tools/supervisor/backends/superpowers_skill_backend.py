"""
Format Factory — Superpowers Skill Backend (Stub)
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Classifies Superpowers plugin availability honestly.
SUPERPOWERS_LOCAL_PLUGIN_NOT_FOUND — .claude/plugins/ absent.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend, ProofLevel
)


class SuperpowersSkillBackend(ExecutionBackend):
    """
    Superpowers local plugin backend.
    Only callable if .claude/plugins/ exists with Superpowers plugin installed.
    Current status: SUPERPOWERS_LOCAL_PLUGIN_NOT_FOUND (.claude/plugins/ absent).
    """

    PLUGIN_PATH = Path(".claude/plugins")

    @property
    def backend_type(self) -> BackendType:
        return BackendType.SUPERPOWERS_LOCAL_PLUGIN

    def discover(self) -> BackendStatus:
        if not self.PLUGIN_PATH.exists():
            return BackendStatus.NOT_FOUND
        # Even if directory exists, plugin must have callable entry
        entries = list(self.PLUGIN_PATH.iterdir())
        if not entries:
            return BackendStatus.NOT_FOUND
        return BackendStatus.SETUP_REQUIRED  # Found but not verified callable

    def can_execute(self, action: dict) -> bool:
        return self.discover() == BackendStatus.VERIFIED_CALLABLE

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        return BackendResult(
            action_id=action.get("action_id", "unknown"),
            backend_used=BackendType.SUPERPOWERS_LOCAL_PLUGIN,
            status="BLOCKED",
            exit_code=3,
            errors=["SUPERPOWERS_LOCAL_PLUGIN_NOT_FOUND: .claude/plugins/ absent. "
                    "Governance intake required before install."],
            selection_reason="Superpowers plugin not installed",
        )
