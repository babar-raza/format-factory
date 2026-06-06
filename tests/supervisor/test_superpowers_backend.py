"""
Format Factory — Superpowers Backend Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
"""
import pytest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.execution_backend import BackendStatus, BackendType
from tools.supervisor.backends.superpowers_skill_backend import SuperpowersSkillBackend


def test_superpowers_not_found():
    backend = SuperpowersSkillBackend()
    status = backend.discover()
    assert status in (BackendStatus.NOT_FOUND, BackendStatus.SETUP_REQUIRED)


def test_superpowers_not_callable():
    backend = SuperpowersSkillBackend()
    assert not backend.can_execute({"action_type": "SKILL_TOOL_INVOKE"})


def test_superpowers_execute_returns_blocked():
    backend = SuperpowersSkillBackend()
    result = backend.execute({"action_id": "t", "action_type": "SKILL_TOOL_INVOKE"}, [])
    assert result.status == "BLOCKED"
    assert result.exit_code == 3


def test_superpowers_backend_type():
    assert SuperpowersSkillBackend().backend_type == BackendType.SUPERPOWERS_LOCAL_PLUGIN
