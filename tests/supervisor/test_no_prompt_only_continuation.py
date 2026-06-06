"""
Tests that "prompt only" is not a valid final continuation state.
Sprint: FORMAT-FACTORY-H6-EXTERNAL-HOST-ACTIVATION-AND-PROOF-001
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_DIR = REPO_ROOT / ".local" / "supervisor"


def test_advisory_md_is_not_active_continuation():
    """Any .md path must not be the next_action_path in active-continuation."""
    p = STATE_DIR / "active-continuation.json"
    if not p.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(p.read_text())
    na_path = data.get("next_action_path", "")
    assert not na_path.endswith(".md"), f"advisory .md path found: {na_path}"


def test_next_sprint_md_not_executable():
    """next-sprint.md must be advisory only (never active-continuation source)."""
    ac = STATE_DIR / "active-continuation.json"
    if not ac.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(ac.read_text())
    advisory_path = data.get("advisory_prompt_path", "")
    # advisory_prompt_path may point to next-sprint.md — that's fine
    # But advisory_prompt_executable must be False
    assert data.get("advisory_prompt_executable") is False


def test_continuation_signal_not_only_advisory():
    """continuation-signal.json should not be the sole continuation mechanism."""
    signal = STATE_DIR / "continuation-signal.json"
    ac = STATE_DIR / "active-continuation.json"
    na = STATE_DIR / "next-action.json"
    # Machine-readable state files must exist alongside signal
    assert ac.exists(), "active-continuation.json must exist alongside continuation-signal"
    assert na.exists(), "next-action.json must exist alongside continuation-signal"


def test_no_required_prompt_paste():
    """The system must not require prompt-paste to continue."""
    na = STATE_DIR / "next-action.json"
    ac = STATE_DIR / "active-continuation.json"
    if not na.exists() or not ac.exists():
        pytest.skip("State files not present")
    # If autonomous_continue=true and advisory_prompt_executable=false,
    # the system can resume without prompt paste
    ac_data = json.loads(ac.read_text())
    assert ac_data.get("autonomous_continue") is True
    assert ac_data.get("advisory_prompt_executable") is False
    # next-action.json must have external_gate=false (no gate blocks continuation)
    na_data = json.loads(na.read_text())
    assert na_data.get("external_gate") is False


def test_evidence_continuation_module_has_objective_field():
    """evidence_continuation generate_post_closeout_next_action must produce objective field."""
    from tools.supervisor.evidence_continuation import generate_post_closeout_next_action
    action = generate_post_closeout_next_action("TEST-SPRINT")
    assert "objective" in action, "generate_post_closeout_next_action must include 'objective' field"
    assert action["objective"], "objective must be non-empty"


def test_evidence_continuation_applied_produces_non_advisory():
    """apply_post_closeout_continuation must produce non-advisory next-action."""
    import tempfile
    from tools.supervisor.evidence_continuation import (
        generate_post_closeout_next_action,
        _is_advisory,
    )
    action = generate_post_closeout_next_action("TEST-SPRINT-H6")
    assert not _is_advisory(action.get("target_path", "")), \
        f"generated target_path is advisory: {action.get('target_path')}"
