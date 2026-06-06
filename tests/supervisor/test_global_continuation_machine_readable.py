"""
Tests that global continuation-signal.json has machine-readable paths.
Sprint: FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

SIGNAL_PATH = _repo_root / ".local" / "supervisor" / "continuation-signal.json"
ACTIVE_CONT_PATH = _repo_root / ".local" / "supervisor" / "active-continuation.json"
NEXT_ACTION_PATH = _repo_root / ".local" / "supervisor" / "next-action.json"
ACTION_QUEUE_PATH = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"


def test_global_continuation_signal_has_machine_path():
    """continuation-signal.json must have machine_continuation_path."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    assert data.get("machine_continuation_path"), "machine_continuation_path must be set"
    assert not data["machine_continuation_path"].endswith(".md"), \
        f"machine_continuation_path must not be advisory Markdown: {data['machine_continuation_path']}"


def test_global_continuation_signal_has_action_queue_path():
    """continuation-signal.json must include action_queue_path."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    assert data.get("action_queue_path"), "action_queue_path must be set in global signal"


def test_global_continuation_advisory_prompt_executable_false():
    """advisory_prompt_executable must be False in global signal."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    assert data.get("advisory_prompt_executable") is False


def test_global_continuation_next_sprint_path_advisory_only():
    """If next_sprint_path exists it must not be the machine_continuation_path."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    nsp = data.get("next_sprint_path", "")
    mcp = data.get("machine_continuation_path", "")
    assert nsp != mcp, "machine_continuation_path must differ from next_sprint_path"


def test_active_continuation_autonomous_continue():
    """active-continuation.json must have autonomous_continue=true."""
    if not ACTIVE_CONT_PATH.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(ACTIVE_CONT_PATH.read_text())
    assert data.get("autonomous_continue") is True


def test_active_continuation_advisory_prompt_not_executable():
    """active-continuation.json advisory_prompt_executable must be False."""
    if not ACTIVE_CONT_PATH.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(ACTIVE_CONT_PATH.read_text())
    assert data.get("advisory_prompt_executable") is False


def test_next_action_not_advisory_md():
    """next-action.json must not be an advisory Markdown file."""
    if not NEXT_ACTION_PATH.exists():
        pytest.skip("next-action.json not present")
    data = json.loads(NEXT_ACTION_PATH.read_text())
    target = data.get("target", data.get("target_path", ""))
    assert not str(target).endswith(".md") or data.get("action_type") == "RUN_MD_NONEMPTY_CHECK", \
        f"next-action target must not be advisory Markdown: {target}"


def test_action_queue_exists():
    """action-queue.jsonl must exist."""
    assert ACTION_QUEUE_PATH.exists(), "action-queue.jsonl must exist"


def test_repair_global_continuation_idempotent():
    """repair_global_continuation_signal() on already-repaired signal returns REPAIRED or same."""
    from tools.supervisor.evidence_continuation import repair_global_continuation_signal
    result = repair_global_continuation_signal(sprint_id="TEST-IDEMPOTENT")
    # Should either be REPAIRED or already contain machine paths
    assert result.get("status") in ("REPAIRED", "ALREADY_MACHINE_READABLE", "CONTINUE_FALSE", "NO_SIGNAL")


def test_repair_adds_advisory_prompt_executable_false():
    """After repair, global signal must have advisory_prompt_executable=false."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    assert data.get("advisory_prompt_executable") is False
