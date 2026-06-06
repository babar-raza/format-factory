"""
Format Factory — Task Master Backend (Stub)
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

L1-L5 readiness model. Task Master "done" NEVER closes a Format Factory taskcard.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend
)

MCP_CONFIG = Path(".vscode/mcp.json")


def get_task_master_layers() -> dict:
    if not MCP_CONFIG.exists():
        return {"L1": False, "L2": "UNKNOWN", "L3": "UNKNOWN", "L4": False, "L5": False, "ready": False}
    try:
        d = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
        servers = d.get("servers", d.get("mcpServers", {}))
        l1 = "task-master-ai" in servers
    except Exception:
        l1 = False
    l4 = bool(os.environ.get("TASK_MASTER_API_KEY", ""))
    return {"L1": l1, "L2": "UNKNOWN", "L3": "UNKNOWN", "L4": l4, "L5": False, "ready": False}


class TaskMasterBackend(ExecutionBackend):
    """Task Master MCP backend — config present, not L5 ready."""

    @property
    def backend_type(self) -> BackendType:
        return BackendType.TASK_MASTER_MCP

    def discover(self) -> BackendStatus:
        layers = get_task_master_layers()
        if not layers["L1"]:
            return BackendStatus.NOT_FOUND
        if not layers["L4"]:
            return BackendStatus.BLOCKED_BY_CREDENTIALS
        return BackendStatus.CONFIG_ONLY

    def can_execute(self, action: dict) -> bool:
        return False  # Not L5 ready

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        layers = get_task_master_layers()
        return BackendResult(
            action_id=action.get("action_id", "unknown"),
            backend_used=BackendType.TASK_MASTER_MCP,
            status="BLOCKED",
            exit_code=3,
            errors=[
                f"TASK_MASTER_NOT_READY: layers={layers}. "
                "NOTE: Task Master 'done' status does NOT close Format Factory taskcards. "
                "Evidence check required."
            ],
        )
