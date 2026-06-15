"""
Tests that unsafe 'git commit/push' items in next-sprint-taskmaster.json
are correctly classified as external-gate-only.
Sprint: FORMAT-FACTORY-H6-QUEUE-DRIVEN-PRODUCT-SOURCE-PILOT-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

TASKMASTER_PATH = _repo_root / "reports" / "supervisor" / "next-sprint-taskmaster.json"
QUARANTINE_REPORT_PATH = (
    _repo_root
    / "reports"
    / "h6-product-source-pilot"
    / "queue"
    / "quarantine-report.json"
)


def _load_taskmaster():
    if not TASKMASTER_PATH.exists():
        return {}
    return json.loads(TASKMASTER_PATH.read_text(encoding="utf-8"))


def test_taskmaster_git_commit_item_has_do_not_self_execute():
    """Any git commit task in next-sprint-taskmaster.json must include 'do NOT self-execute' guard."""
    data = _load_taskmaster()
    if not data:
        pytest.skip("next-sprint-taskmaster.json not present")
    tasks = data.get("tasks", [])
    for task in tasks:
        title = task.get("title", "")
        if "git commit" in title.lower():
            assert "do not self-execute" in title.lower() or task.get("status") in (
                "external-gate",
                "agent-owned",
            ), f"git commit task missing guard: {title}"


def test_quarantine_report_exists():
    """quarantine-report.json must exist documenting null-action-type removal."""
    assert QUARANTINE_REPORT_PATH.exists(), "quarantine-report.json not found"


def test_quarantine_report_removed_null_items():
    """quarantine-report.json must show at least 1 item was removed."""
    if not QUARANTINE_REPORT_PATH.exists():
        pytest.skip("quarantine-report.json not present")
    data = json.loads(QUARANTINE_REPORT_PATH.read_text())
    items = data.get("quarantined_items", [])
    assert len(items) >= 1, "Expected at least 1 quarantined item"


def test_quarantine_report_null_item_was_c31d2171():
    """The quarantined item must be c31d2171 (the null-action_type item from Sprint 7)."""
    if not QUARANTINE_REPORT_PATH.exists():
        pytest.skip("quarantine-report.json not present")
    data = json.loads(QUARANTINE_REPORT_PATH.read_text())
    ids = [i.get("action_id") for i in data.get("quarantined_items", [])]
    assert "c31d2171" in ids, f"Expected c31d2171 in quarantined items, got {ids}"


def test_queue_has_no_null_after_quarantine():
    """Live queue must have zero items missing both action_type and item_type after quarantine."""
    queue_path = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"
    if not queue_path.exists():
        pytest.skip("action-queue.jsonl not present")
    lines = queue_path.read_text(encoding="utf-8").splitlines()
    items = [json.loads(l) for l in lines if l.strip()]
    null_items = [i for i in items if i.get("action_type") is None and i.get("item_type") is None]
    assert null_items == [], f"Found items with neither action_type nor item_type: {null_items}"


def test_no_git_push_in_action_queue():
    """action-queue.jsonl must not contain any GIT_PUSH action type."""
    queue_path = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"
    if not queue_path.exists():
        pytest.skip("action-queue.jsonl not present")
    lines = queue_path.read_text(encoding="utf-8").splitlines()
    items = [json.loads(l) for l in lines if l.strip()]
    push_items = [i for i in items if i.get("action_type") == "GIT_PUSH"]
    assert push_items == [], f"GIT_PUSH must not appear in queue: {push_items}"


def test_no_gate_approval_in_action_queue():
    """action-queue.jsonl must not contain gate approval actions."""
    queue_path = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"
    if not queue_path.exists():
        pytest.skip("action-queue.jsonl not present")
    lines = queue_path.read_text(encoding="utf-8").splitlines()
    items = [json.loads(l) for l in lines if l.strip()]
    gate_items = [
        i for i in items if "GATE" in str(i.get("action_type", "")).upper()
    ]
    assert gate_items == [], f"Gate approval actions must not be in queue: {gate_items}"
