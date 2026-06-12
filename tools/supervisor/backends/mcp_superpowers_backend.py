"""
Format Factory — MCP Superpowers Backend (Stub)
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001

Classifies MCP readiness using L1-L5 model.
Config-only (L1) is NOT callable. Requires L5 to execute.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from tools.supervisor.execution_backend import (
    BackendResult, BackendStatus, BackendType, ExecutionBackend
)


class McpSuperpowersBackend(ExecutionBackend):
    """MCP superpowers backend — config present, not yet callable."""

    MCP_CONFIG_PATH = Path(".vscode/mcp.json")

    @property
    def backend_type(self) -> BackendType:
        return BackendType.MCP_SUPERPOWERS

    def _get_mcp_layers(self) -> dict:
        if not self.MCP_CONFIG_PATH.exists():
            return {"L1": False, "L2": False, "L3": False, "L4": False, "L5": False}
        try:
            d = json.loads(self.MCP_CONFIG_PATH.read_text(encoding="utf-8"))
            servers = d.get("servers", d.get("mcpServers", {}))
            l1 = "task-master-ai" in servers or "claude-flow" in servers
        except Exception:
            l1 = False
        # L2-L5 cannot be verified from inside session
        l4_key = os.environ.get("TASK_MASTER_API_KEY", "")
        return {"L1": l1, "L2": "UNKNOWN", "L3": "UNKNOWN", "L4": bool(l4_key), "L5": False}

    def discover(self) -> BackendStatus:
        layers = self._get_mcp_layers()
        if not layers["L1"]:
            return BackendStatus.NOT_FOUND
        # L1 only = config present but not callable
        return BackendStatus.CONFIG_ONLY

    def can_execute(self, action: dict) -> bool:
        return False  # Never callable with current config-only status

    def execute(self, action: dict, allowed_write_roots) -> BackendResult:
        layers = self._get_mcp_layers()
        return BackendResult(
            action_id=action.get("action_id", "unknown"),
            backend_used=BackendType.MCP_SUPERPOWERS,
            status="BLOCKED",
            exit_code=3,
            errors=[
                f"MCP_NOT_READY: L1={layers['L1']}, L2={layers['L2']}, "
                f"L3={layers['L3']}, L4={layers['L4']}, L5={layers['L5']}. "
                "Set TASK_MASTER_API_KEY and start MCP daemon for L5."
            ],
        )
