"""
Format Factory — Backend Selector Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_root))

from tools.supervisor.execution_backend import BackendType
from tools.supervisor.backend_selector import select_backend
from tools.supervisor.backends.local_deterministic_backend import LocalDeterministicBackend
from tools.supervisor.backends.superpowers_skill_backend import SuperpowersSkillBackend
from tools.supervisor.backends.mcp_superpowers_backend import McpSuperpowersBackend


def test_selector_picks_local_when_all_unavailable():
    """When all higher-priority backends are unavailable, selects LOCAL_DETERMINISTIC."""
    action = {
        "action_id": "sel-001",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "test",
        "preferred_backend": "SUPERPOWERS_LOCAL_PLUGIN",
    }
    backends = [
        SuperpowersSkillBackend(),
        McpSuperpowersBackend(),
        LocalDeterministicBackend(),
    ]
    backend, trace = select_backend(action, backends)
    assert backend is not None
    assert backend.backend_type == BackendType.LOCAL_DETERMINISTIC
    # Higher priority backends should be in skipped list
    skipped_names = [s["backend"] for s in trace.skipped]
    assert BackendType.SUPERPOWERS_LOCAL_PLUGIN.value in skipped_names


def test_selector_blocks_forbidden_actions():
    """Selector blocks forbidden action types."""
    for ft in ["GIT_PUSH", "GATE_11_APPROVAL", "PACKAGE_PUBLISH"]:
        action = {
            "action_id": "sel-forbidden",
            "action_type": ft,
            "objective": "forbidden",
            "preferred_backend": "LOCAL_DETERMINISTIC",
        }
        _, trace = select_backend(action, [LocalDeterministicBackend()])
        assert trace.blocked, f"{ft} must be blocked"


def test_selector_blocks_external_gate():
    """external_gate=true blocks autonomous execution."""
    action = {
        "action_id": "sel-gate",
        "action_type": "MANUAL_EXTERNAL_GATE",
        "objective": "gate",
        "preferred_backend": "MANUAL_EXTERNAL_GATE",
        "external_gate": True,
    }
    _, trace = select_backend(action, [LocalDeterministicBackend()])
    assert trace.blocked


def test_selector_trace_explains_skips():
    """Selection trace explains why each backend was skipped."""
    action = {
        "action_id": "sel-trace",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "test",
        "preferred_backend": "SUPERPOWERS_LOCAL_PLUGIN",
    }
    backends = [SuperpowersSkillBackend(), McpSuperpowersBackend(), LocalDeterministicBackend()]
    _, trace = select_backend(action, backends)
    assert len(trace.skipped) >= 2
    for skip in trace.skipped:
        assert "reason" in skip and skip["reason"]


def test_selector_config_only_not_callable():
    """CONFIG_ONLY backend (MCP L1) is skipped, not selected."""
    action = {
        "action_id": "sel-mcp",
        "action_type": "MCP_TOOL_CALL",
        "objective": "call MCP",
        "preferred_backend": "MCP_SUPERPOWERS",
    }
    backends = [McpSuperpowersBackend(), LocalDeterministicBackend()]
    backend, trace = select_backend(action, backends)
    # MCP is CONFIG_ONLY → skip to LOCAL_DETERMINISTIC
    # LOCAL_DETERMINISTIC can't do MCP_TOOL_CALL either → no backend or blocked
    # (MCP_TOOL_CALL is not in LOCAL_DETERMINISTIC.SUPPORTED_ACTIONS)
    skipped_names = [s["backend"] for s in trace.skipped]
    assert BackendType.MCP_SUPERPOWERS.value in skipped_names
