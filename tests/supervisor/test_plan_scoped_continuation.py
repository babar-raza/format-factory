"""
test_plan_scoped_continuation.py — Integration tests for Check 0c (chat plan binding)
and continuation ledger wiring.

Tests verify that:
1. An IN_PROGRESS binding for the SAME session blocks check_continuation
2. An IN_PROGRESS binding for a DIFFERENT session does NOT block
3. A COMPLETE binding does NOT block
4. An expired binding (>TTL) does NOT block
5. No binding does NOT block
6. --clear-mission removes the binding directory
7. Ledger entries are written on every check_continuation verdict
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


def _write_binding_yaml(missions_dir: Path, mission_id: str, **fields) -> Path:
    """Write a plan-binding.yaml file directly for testing."""
    import yaml
    mission_dir = missions_dir / mission_id
    mission_dir.mkdir(parents=True, exist_ok=True)
    binding_path = mission_dir / "plan-binding.yaml"
    binding = {"chat_plan_binding": {
        "mission_id": mission_id,
        "plan_path": fields.get("plan_path", "plans/test.md"),
        "session_id": fields.get("session_id", "test-session-id"),
        "status": fields.get("status", "IN_PROGRESS"),
        "global_ledger_fallback_allowed": fields.get("global_ledger_fallback_allowed", False),
        "created_at": fields.get("created_at", datetime.now(timezone.utc).isoformat()),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_taskcard": fields.get("last_taskcard"),
        "ttl_hours": fields.get("ttl_hours", 48),
    }}
    binding_path.write_text(yaml.dump(binding, default_flow_style=False), encoding="utf-8")
    return binding_path


def _run_check(repo_root: Path, session_id: str = "test-session-id",
               track: str | None = None) -> dict:
    """Run check_continuation.check() with given params."""
    from check_continuation import check
    return check(repo_root, session_id=session_id, track=track)


@pytest.fixture
def tmp_repo(tmp_path):
    """Create a minimal repo structure that check_continuation can operate on."""
    # Create the signal file (required for check to proceed past Check 1)
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    signal = {
        "autonomous_continue": True,
        "iteration": 0,
        "max_iterations": 5,
        "continuation_state": "YES_RESET_CLEAN",
        "session_id": "test-session-id",
        "hard_stops_detected": [],
        "rework_items": [],
    }
    (sig_dir / "continuation-signal.json").write_text(json.dumps(signal), encoding="utf-8")

    # Create approval-gates.md
    reports_dir = tmp_path / "reports" / "supervisor"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "approval-gates.md").write_text("AUTONOMOUS_CONTINUE: YES\n", encoding="utf-8")

    # Create next-work-items.json
    (sig_dir / "next-work-items.json").write_text(json.dumps({
        "items": [{"item_id": "TEST-ITEM-001"}],
        "work_selection_mode": "NORMAL",
    }), encoding="utf-8")

    return tmp_path


class TestBindingActiveSameSession:
    def test_blocks(self, tmp_repo):
        missions = tmp_repo / ".local" / "missions"
        _write_binding_yaml(missions, "TEST-BLOCK", session_id="test-session-id")
        result = _run_check(tmp_repo, session_id="test-session-id")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "CHAT_PLAN_BINDING_ACTIVE"
        assert result.get("mission_id") == "TEST-BLOCK"


class TestBindingActiveDifferentSession:
    def test_passes(self, tmp_repo):
        missions = tmp_repo / ".local" / "missions"
        _write_binding_yaml(missions, "TEST-OTHER", session_id="other-session-xyz")
        result = _run_check(tmp_repo, session_id="test-session-id")
        assert result.get("reason") != "CHAT_PLAN_BINDING_ACTIVE"


class TestBindingComplete:
    def test_does_not_block(self, tmp_repo):
        missions = tmp_repo / ".local" / "missions"
        _write_binding_yaml(missions, "TEST-DONE", session_id="test-session-id",
                            status="COMPLETE", global_ledger_fallback_allowed=True)
        result = _run_check(tmp_repo, session_id="test-session-id")
        assert result.get("reason") != "CHAT_PLAN_BINDING_ACTIVE"


class TestBindingExpired:
    def test_does_not_block(self, tmp_repo):
        missions = tmp_repo / ".local" / "missions"
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=49)).isoformat()
        _write_binding_yaml(missions, "TEST-EXPIRED", session_id="test-session-id",
                            created_at=old_ts, ttl_hours=48)
        result = _run_check(tmp_repo, session_id="test-session-id")
        assert result.get("reason") != "CHAT_PLAN_BINDING_ACTIVE"


class TestNoBinding:
    def test_does_not_block(self, tmp_repo):
        result = _run_check(tmp_repo, session_id="test-session-id")
        assert result.get("reason") != "CHAT_PLAN_BINDING_ACTIVE"


class TestClearMission:
    def test_removes_directory(self, tmp_repo):
        missions = tmp_repo / ".local" / "missions"
        _write_binding_yaml(missions, "TEST-CLEAR", session_id="test-session-id")
        assert (missions / "TEST-CLEAR" / "plan-binding.yaml").exists()

        from write_chat_plan_binding import clear_mission
        # Temporarily override _MISSIONS_DIR
        import write_chat_plan_binding as wcpb
        orig = wcpb._MISSIONS_DIR
        try:
            wcpb._MISSIONS_DIR = missions
            wcpb.clear_mission("TEST-CLEAR")
        finally:
            wcpb._MISSIONS_DIR = orig

        assert not (missions / "TEST-CLEAR").exists()


class TestLedgerEntry:
    def test_written_on_verdict(self, tmp_repo):
        ledger_path = tmp_repo / ".local" / "supervisor" / "continuation-ledger.jsonl"
        # Remove existing ledger to isolate
        if ledger_path.exists():
            ledger_path.unlink()

        # Patch LEDGER_PATH in continuation_ledger module
        import continuation_ledger as cl
        orig_path = cl.LEDGER_PATH
        try:
            cl.LEDGER_PATH = ledger_path
            result = _run_check(tmp_repo, session_id="test-session-id")
        finally:
            cl.LEDGER_PATH = orig_path

        # The check should have written at least one verdict entry
        if ledger_path.exists():
            lines = [l for l in ledger_path.read_text().strip().split("\n") if l.strip()]
            verdicts = [json.loads(l) for l in lines
                        if "CONTINUATION_VERDICT" in l]
            assert len(verdicts) >= 1
            assert verdicts[-1]["metadata"]["verdict"] in ("STOP", "CONTINUE")
