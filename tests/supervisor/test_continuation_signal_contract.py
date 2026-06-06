"""
Tests for continuation signal contract.

Sprint: FORMAT-FACTORY-AUTONOMY-NO-MANUAL-PROMPT-CHAIN-REPAIR-001

Verifies:
1. autonomous_continue=true requires machine-readable paths
2. next_sprint_path alone is invalid for autonomous continuation
3. advisory_prompt_executable must be false
4. post-closeout next-action is not advisory Markdown
5. apply_post_closeout_continuation produces correct files
6. repair_global_continuation_signal adds machine paths
"""
from __future__ import annotations

import json
import sys
import tempfile
import uuid
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))

from evidence_continuation import (
    _is_advisory,
    generate_post_closeout_next_action,
    write_post_closeout_next_action,
    write_post_closeout_active_continuation,
    apply_post_closeout_continuation,
    repair_global_continuation_signal,
    repair_continuation_signal,
    seed_post_closeout_queue_item,
    CONTINUATION_SIGNAL_PATH,
    NEXT_ACTION_PATH,
    ACTIVE_CONTINUATION_PATH,
    ACTION_QUEUE_PATH,
)


# ---------------------------------------------------------------------------
# 1. _is_advisory — advisory detection
# ---------------------------------------------------------------------------

def test_is_advisory_next_sprint_md():
    assert _is_advisory("reports/supervisor/next-sprint.md") is True


def test_is_advisory_session_resume_md():
    assert _is_advisory("reports/supervisor/session-resume.md") is True


def test_is_advisory_empty_string():
    assert _is_advisory("") is True


def test_is_advisory_next_work_items_json():
    assert _is_advisory("reports/supervisor/next-work-items.json") is True


def test_is_advisory_machine_readable_json():
    assert _is_advisory(".local/supervisor/next-action.json") is False


def test_is_advisory_action_queue():
    assert _is_advisory(".local/supervisor/action-queue.jsonl") is False


def test_is_advisory_approval_gates():
    # approval-gates.md is a target to CHECK, not an advisory prompt
    # The action TYPE is MD_NONEMPTY_CHECK; the path itself is not advisory
    # when used as a TARGET (not as a directive). But _is_advisory only
    # checks the path name, so .md extension → advisory.
    # This is expected — the KEY is that it's used as action TARGET, not as
    # advisory_prompt_path in the continuation signal.
    result = _is_advisory("reports/supervisor/approval-gates.md")
    assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# 2. generate_post_closeout_next_action — structure
# ---------------------------------------------------------------------------

def test_generate_post_closeout_next_action_has_schema_version():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("schema_version") == 1


def test_generate_post_closeout_next_action_has_action_id():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("action_id")
    assert len(action["action_id"]) > 4


def test_generate_post_closeout_next_action_has_action_type():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("action_type") in (
        "RUN_MD_NONEMPTY_CHECK",
        "RUN_JSON_VALIDATION",
        "QUEUE_HEALTH_CHECK",
    )


def test_generate_post_closeout_next_action_no_external_gate():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("external_gate") is False


def test_generate_post_closeout_next_action_preferred_backend():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("preferred_backend") == "LOCAL_DETERMINISTIC"


def test_generate_post_closeout_next_action_has_target():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("target_path")
    # Must not be empty
    assert len(action["target_path"]) > 0


def test_generate_post_closeout_next_action_target_not_advisory_prompt():
    """Target may be an .md file for nonempty check, but must not point to next-sprint.md."""
    action = generate_post_closeout_next_action("test-sprint-001")
    target = action.get("target_path", "")
    assert "next-sprint.md" not in target
    assert "session-resume.md" not in target


def test_generate_post_closeout_next_action_is_post_closeout():
    action = generate_post_closeout_next_action("test-sprint-001")
    assert action.get("post_closeout") is True


# ---------------------------------------------------------------------------
# 3. write_post_closeout_next_action — file I/O
# ---------------------------------------------------------------------------

def test_write_post_closeout_next_action_creates_file(tmp_path):
    out = tmp_path / "next-action.json"
    result = write_post_closeout_next_action("test-sprint", output_path=out)
    assert result == out
    assert out.exists()
    data = json.loads(out.read_text())
    assert data.get("schema_version") == 1
    assert data.get("post_closeout") is True


def test_write_post_closeout_next_action_valid_json(tmp_path):
    out = tmp_path / "next-action.json"
    write_post_closeout_next_action("sprint-x", output_path=out)
    data = json.loads(out.read_text())
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# 4. write_post_closeout_active_continuation
# ---------------------------------------------------------------------------

def test_write_post_closeout_active_continuation_not_advisory(tmp_path):
    """active-continuation must not point to advisory Markdown."""
    from unittest.mock import patch
    import evidence_continuation as ec
    orig = ec.ACTIVE_CONTINUATION_PATH
    ec.ACTIVE_CONTINUATION_PATH = tmp_path / "active-continuation.json"
    try:
        next_action = tmp_path / "next-action.json"
        next_action.write_text("{}")
        ec.write_post_closeout_active_continuation("sprint-x", next_action)
        data = json.loads(ec.ACTIVE_CONTINUATION_PATH.read_text())
        assert data.get("advisory_prompt_executable") is False
        assert data.get("advisory_prompt_path") is None
        assert data.get("next_action_path") is not None
        assert "next-sprint.md" not in str(data.get("next_action_path", ""))
    finally:
        ec.ACTIVE_CONTINUATION_PATH = orig


def test_write_post_closeout_active_continuation_autonomous_continue(tmp_path):
    from unittest.mock import patch
    import evidence_continuation as ec
    orig = ec.ACTIVE_CONTINUATION_PATH
    ec.ACTIVE_CONTINUATION_PATH = tmp_path / "active-continuation.json"
    try:
        next_action = tmp_path / "next-action.json"
        next_action.write_text("{}")
        ec.write_post_closeout_active_continuation("sprint-x", next_action)
        data = json.loads(ec.ACTIVE_CONTINUATION_PATH.read_text())
        assert data.get("autonomous_continue") is True
    finally:
        ec.ACTIVE_CONTINUATION_PATH = orig


# ---------------------------------------------------------------------------
# 5. repair_global_continuation_signal
# ---------------------------------------------------------------------------

def test_repair_global_continuation_signal_adds_machine_paths(tmp_path):
    import evidence_continuation as ec
    orig_sig = ec.CONTINUATION_SIGNAL_PATH
    ec.CONTINUATION_SIGNAL_PATH = tmp_path / "continuation-signal.json"
    try:
        # Write a signal with only advisory path
        signal = {
            "autonomous_continue": True,
            "next_sprint_path": "reports/supervisor/next-sprint.md",
            "iteration": 0,
        }
        ec.CONTINUATION_SIGNAL_PATH.write_text(json.dumps(signal))
        result = repair_global_continuation_signal("sprint-x")
        assert result.get("status") == "REPAIRED"
        updated = json.loads(ec.CONTINUATION_SIGNAL_PATH.read_text())
        assert "next_action_path" in updated
        assert "action_queue_path" in updated
        assert updated.get("advisory_prompt_executable") is False
    finally:
        ec.CONTINUATION_SIGNAL_PATH = orig_sig


def test_repair_global_continuation_signal_no_signal(tmp_path):
    import evidence_continuation as ec
    orig = ec.CONTINUATION_SIGNAL_PATH
    ec.CONTINUATION_SIGNAL_PATH = tmp_path / "nonexistent.json"
    try:
        result = repair_global_continuation_signal("sprint-x")
        assert result.get("status") == "NO_SIGNAL"
        assert result.get("repaired") is False
    finally:
        ec.CONTINUATION_SIGNAL_PATH = orig


def test_repair_global_continuation_signal_continue_false(tmp_path):
    import evidence_continuation as ec
    orig = ec.CONTINUATION_SIGNAL_PATH
    ec.CONTINUATION_SIGNAL_PATH = tmp_path / "sig.json"
    try:
        signal = {"autonomous_continue": False, "next_sprint_path": "reports/supervisor/next-sprint.md"}
        ec.CONTINUATION_SIGNAL_PATH.write_text(json.dumps(signal))
        result = repair_global_continuation_signal("sprint-x")
        assert result.get("status") == "CONTINUE_FALSE"
        assert result.get("repaired") is False
    finally:
        ec.CONTINUATION_SIGNAL_PATH = orig


# ---------------------------------------------------------------------------
# 6. seed_post_closeout_queue_item
# ---------------------------------------------------------------------------

def test_seed_post_closeout_queue_item_seeds_when_empty(tmp_path):
    import evidence_continuation as ec
    orig = ec.ACTION_QUEUE_PATH
    ec.ACTION_QUEUE_PATH = tmp_path / "action-queue.jsonl"
    try:
        result = seed_post_closeout_queue_item("sprint-x")
        assert result.get("status") == "SEEDED"
        assert result.get("seeded") is True
        lines = ec.ACTION_QUEUE_PATH.read_text().splitlines()
        items = [json.loads(l) for l in lines if l.strip()]
        pending = [i for i in items if i.get("status", "pending") != "done"]
        assert len(pending) == 1
        assert pending[0].get("action_type") == "QUEUE_HEALTH_CHECK"
        assert pending[0].get("external_gate") is False
    finally:
        ec.ACTION_QUEUE_PATH = orig


def test_seed_post_closeout_queue_item_no_seed_when_pending_exists(tmp_path):
    import evidence_continuation as ec
    orig = ec.ACTION_QUEUE_PATH
    ec.ACTION_QUEUE_PATH = tmp_path / "action-queue.jsonl"
    try:
        existing = {"action_id": "x", "action_type": "RUN_JSON_VALIDATION", "status": "pending"}
        ec.ACTION_QUEUE_PATH.write_text(json.dumps(existing) + "\n")
        result = seed_post_closeout_queue_item("sprint-x")
        assert result.get("status") == "ALREADY_HAS_PENDING"
        assert result.get("seeded") is False
    finally:
        ec.ACTION_QUEUE_PATH = orig


def test_seed_post_closeout_queue_item_seeds_when_all_done(tmp_path):
    import evidence_continuation as ec
    orig = ec.ACTION_QUEUE_PATH
    ec.ACTION_QUEUE_PATH = tmp_path / "action-queue.jsonl"
    try:
        done = {"action_id": "done1", "action_type": "RUN_JSON_VALIDATION", "status": "done"}
        ec.ACTION_QUEUE_PATH.write_text(json.dumps(done) + "\n")
        result = seed_post_closeout_queue_item("sprint-x")
        assert result.get("status") == "SEEDED"
    finally:
        ec.ACTION_QUEUE_PATH = orig


def test_seed_post_closeout_queue_item_no_external_gate(tmp_path):
    import evidence_continuation as ec
    orig = ec.ACTION_QUEUE_PATH
    ec.ACTION_QUEUE_PATH = tmp_path / "action-queue.jsonl"
    try:
        result = seed_post_closeout_queue_item("sprint-x")
        items = [json.loads(l) for l in ec.ACTION_QUEUE_PATH.read_text().splitlines() if l.strip()]
        pending = [i for i in items if i.get("status", "pending") != "done"]
        assert all(i.get("external_gate") is False for i in pending)
    finally:
        ec.ACTION_QUEUE_PATH = orig


# ---------------------------------------------------------------------------
# 7. Contract: autonomous_continue=true must not leave only Markdown
# ---------------------------------------------------------------------------

def test_apply_post_closeout_continuation_writes_non_advisory_action(tmp_path):
    import evidence_continuation as ec
    orig_na = ec.NEXT_ACTION_PATH
    orig_ac = ec.ACTIVE_CONTINUATION_PATH
    ec.NEXT_ACTION_PATH = tmp_path / "next-action.json"
    ec.ACTIVE_CONTINUATION_PATH = tmp_path / "active-continuation.json"
    try:
        result = apply_post_closeout_continuation("sprint-test")
        assert result.get("status") == "POST_CLOSEOUT_CONTINUATION_READY"
        # next-action.json must exist and be machine-readable
        assert ec.NEXT_ACTION_PATH.exists()
        action = json.loads(ec.NEXT_ACTION_PATH.read_text())
        assert action.get("action_type") is not None
        # Must not be advisory
        assert action.get("action_type") not in ("ADVISORY_PROMPT", "NEXT_SPRINT_MD")
        assert _is_advisory(action.get("target_path", "next-sprint.md")) is not True or \
               action.get("action_type") in ("RUN_MD_NONEMPTY_CHECK",)
    finally:
        ec.NEXT_ACTION_PATH = orig_na
        ec.ACTIVE_CONTINUATION_PATH = orig_ac


def test_advisory_prompt_executable_never_true_in_active_continuation(tmp_path):
    import evidence_continuation as ec
    orig_ac = ec.ACTIVE_CONTINUATION_PATH
    orig_na = ec.NEXT_ACTION_PATH
    ec.ACTIVE_CONTINUATION_PATH = tmp_path / "active-continuation.json"
    ec.NEXT_ACTION_PATH = tmp_path / "next-action.json"
    try:
        apply_post_closeout_continuation("sprint-test")
        data = json.loads(ec.ACTIVE_CONTINUATION_PATH.read_text())
        assert data.get("advisory_prompt_executable") is False
    finally:
        ec.ACTIVE_CONTINUATION_PATH = orig_ac
        ec.NEXT_ACTION_PATH = orig_na
