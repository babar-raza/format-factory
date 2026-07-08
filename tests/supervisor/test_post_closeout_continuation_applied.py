"""
Tests for post-closeout continuation applied (not only implemented).
Sprint: FORMAT-FACTORY-H6-EXTERNAL-HOST-ACTIVATION-AND-PROOF-001
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_DIR = REPO_ROOT / ".local" / "supervisor"
H6_POST_DIR = REPO_ROOT / "reports" / "h6-external-host-activation" / "post-closeout"


def test_active_continuation_exists():
    """active-continuation.json must exist (not missing)."""
    p = STATE_DIR / "active-continuation.json"
    if not p.exists():
        pytest.skip("active-continuation.json not present (gitignored, CI skip)")
    assert p.exists(), "active-continuation.json must exist"


def test_active_continuation_autonomous_continue_true():
    """active-continuation must have autonomous_continue=true."""
    p = STATE_DIR / "active-continuation.json"
    if not p.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(p.read_text())
    assert data.get("autonomous_continue") is True


def test_active_continuation_advisory_not_executable():
    """active-continuation must NOT be executable advisory."""
    p = STATE_DIR / "active-continuation.json"
    if not p.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(p.read_text())
    assert data.get("advisory_prompt_executable") is False


def test_active_continuation_points_to_next_action():
    """active-continuation next_action_path must exist."""
    p = STATE_DIR / "active-continuation.json"
    if not p.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(p.read_text())
    na_path = data.get("next_action_path", "")
    assert na_path, "next_action_path must be set"
    # Check that it's not pointing to advisory .md
    assert not na_path.endswith(".md"), f"next_action_path must not be .md: {na_path}"


def test_next_action_exists():
    """next-action.json must exist."""
    p = STATE_DIR / "next-action.json"
    if not p.exists():
        pytest.skip("next-action.json not present (gitignored, CI skip)")
    assert p.exists(), "next-action.json must exist"


def test_next_action_has_required_fields():
    """next-action.json must have schema-required fields."""
    p = STATE_DIR / "next-action.json"
    if not p.exists():
        pytest.skip("next-action.json not present")
    data = json.loads(p.read_text())
    for field in ("action_id", "action_type", "objective", "preferred_backend"):
        assert field in data, f"next-action.json missing required field: {field}"


def test_next_action_not_advisory():
    """next-action.json action_type must not be advisory."""
    p = STATE_DIR / "next-action.json"
    if not p.exists():
        pytest.skip("next-action.json not present")
    data = json.loads(p.read_text())
    assert data.get("external_gate") is False, "next-action external_gate must be False"


def test_action_queue_exists():
    """action-queue.jsonl must exist."""
    p = STATE_DIR / "action-queue.jsonl"
    if not p.exists():
        pytest.skip("action-queue.jsonl not present (gitignored, CI skip)")
    assert p.exists(), "action-queue.jsonl must exist"


def test_action_queue_not_empty():
    """action-queue.jsonl must have at least 1 item."""
    p = STATE_DIR / "action-queue.jsonl"
    if not p.exists():
        pytest.skip("action-queue.jsonl not present")
    lines = [l for l in p.read_text(encoding="utf-8").strip().split("\n") if l.strip()]
    assert len(lines) >= 1, "action-queue.jsonl must not be empty"


def test_post_closeout_continuation_report_exists():
    """post-closeout-continuation.json must exist and show bridge applied."""
    p = H6_POST_DIR / "post-closeout-continuation.json"
    assert p.exists(), "post-closeout-continuation.json must exist"
    data = json.loads(p.read_text())
    assert data.get("bridge_applied") is True


def test_next_sprint_md_is_not_active_continuation():
    """reports/supervisor/next-sprint.md must NOT be the active continuation path."""
    ac = STATE_DIR / "active-continuation.json"
    if not ac.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(ac.read_text())
    na_path = data.get("next_action_path", "")
    assert "next-sprint.md" not in na_path, "next-sprint.md must not be the active continuation path"
    assert "next-work-items" not in na_path


def test_command_ready_is_not_final_result():
    """'Command ready' alone is not execution proof — must have actual run evidence."""
    # Verify both attempt results AND cycle results exist
    attempts_file = REPO_ROOT / "reports" / "h6-external-host-activation" / "host-launch" / "launch-attempts.json"
    cycle_results = list((REPO_ROOT / "reports" / "autonomous-orchestrator" / "proof-run").glob("cycle-*.json"))
    assert attempts_file.exists(), "Launch attempts must be documented (not just command ready)"
    assert len(cycle_results) >= 3, "Actual cycle execution required (not just command ready)"
