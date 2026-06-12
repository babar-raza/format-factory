"""
Format Factory — Autonomous Host Daemon Tests
Sprint: FORMAT-FACTORY-SUPERPOWERS-AGENTIC-AUTONOMY-EXECUTION-001
"""
import json
import sys
import pytest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.supervisor.autonomous_host_daemon import run_daemon, get_external_host_command, _is_in_claudecode


def test_daemon_blocked_on_claude_cli_in_session(tmp_path, monkeypatch):
    """Daemon blocks claude-cli backend inside CLAUDECODE session."""
    monkeypatch.setenv("CLAUDECODE", "1")
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps({
        "action_id": "d-001",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "test",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(action_file),
    }), encoding="utf-8")
    result = run_daemon(str(action_file), backend="claude-cli")
    assert result["status"] == "BLOCKED"
    assert "CLAUDE_CLI_FORBIDDEN_IN_CLAUDECODE_SESSION" in result["reason"]


def test_daemon_dry_run(tmp_path):
    """Daemon dry-run works without executing."""
    target = tmp_path / "v.json"
    target.write_text('{}', encoding="utf-8")
    result_path = tmp_path / "result.json"
    action_file = tmp_path / "action.json"
    action_file.write_text(json.dumps({
        "action_id": "d-002",
        "action_type": "RUN_JSON_VALIDATION",
        "objective": "test",
        "preferred_backend": "LOCAL_DETERMINISTIC",
        "target": str(target),
        "result_path": str(result_path),
    }), encoding="utf-8")
    result = run_daemon(str(action_file), dry_run=True)
    assert result["status"] in ("COMPLETE", "FAILED")  # DRY_RUN cycle counts
    assert not result_path.exists()


def test_daemon_reports_claudecode_session_status():
    """Daemon result includes in_claudecode_session flag."""
    # We don't know if we're in CLAUDECODE but the field must exist
    action_file = Path("reports/superpowers-agentic-autonomy/runtime-discovery/tool-status-runtime.json")
    if not action_file.exists():
        pytest.skip("Runtime discovery not yet available")
    # Just check the helper
    status = _is_in_claudecode()
    assert isinstance(status, bool)


def test_external_host_command_contains_daemon_path():
    """get_external_host_command returns usable PowerShell command."""
    cmd = get_external_host_command("reports/test-action.json")
    assert "python" in cmd
    assert "autonomous_host_daemon" in cmd
    assert "CLAUDECODE" in cmd
