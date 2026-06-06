"""
Format Factory — MCP Superpowers Backend Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
"""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.execution_backend import BackendStatus, BackendType
from tools.supervisor.backends.mcp_superpowers_backend import McpSuperpowersBackend


def test_mcp_config_only_not_callable():
    backend = McpSuperpowersBackend()
    status = backend.discover()
    assert status in (BackendStatus.CONFIG_ONLY, BackendStatus.NOT_FOUND)
    assert status != BackendStatus.VERIFIED_CALLABLE


def test_mcp_cannot_execute():
    backend = McpSuperpowersBackend()
    assert not backend.can_execute({"action_type": "MCP_TOOL_CALL"})


def test_mcp_execute_returns_blocked():
    backend = McpSuperpowersBackend()
    result = backend.execute({"action_id": "t", "action_type": "MCP_TOOL_CALL"}, [])
    assert result.status == "BLOCKED"
    assert any("MCP_NOT_READY" in e for e in result.errors)


def test_mcp_backend_type():
    assert McpSuperpowersBackend().backend_type == BackendType.MCP_SUPERPOWERS
