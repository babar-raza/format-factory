"""Tests for TERMINAL_CLOSED premature-closure prevention.

Task: TC-TCF-009 (eager-snuggling-sifakis)
Mission: TC-FORENSICS-TERMINAL-20260623

Covers:
  - Plan file taskcard parser (TC-TCF-003)
  - Error fallback safe behavior (TC-TCF-004)
  - COMPLETION_CANDIDATE state (TC-TCF-005)
  - Closure contract validation (TC-TCF-006)
  - Governed reopening (TC-TCF-007)
  - Premature closure path negative controls
  - Pilot simulations A/B/D/G/H/I/L
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))

from lifecycle_audit import (  # type: ignore[import]
    build_closure_contract,
    compute_plan_hash,
    parse_plan_taskcards,
    run_lifecycle_audit,
)


# ---------------------------------------------------------------------------
# Plan file taskcard parser tests (TC-TCF-003)
# ---------------------------------------------------------------------------


class TestParsePlanTaskcards:
    """Tests for parse_plan_taskcards()."""

    def test_table_format(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n"
            "| TC-FOO-001 | CLOSED | Task 1 |\n"
            "| TC-FOO-002 | OPEN | Task 2 |\n"
            "| TC-FOO-003 | CLOSED | Task 3 |\n"
        )
        result = parse_plan_taskcards(plan)
        assert len(result) == 3
        assert result[0] == {"tc_id": "TC-FOO-001", "status": "CLOSED"}
        assert result[1] == {"tc_id": "TC-FOO-002", "status": "OPEN"}
        assert result[2] == {"tc_id": "TC-FOO-003", "status": "CLOSED"}

    def test_block_format(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text(
            "# Plan\n\n"
            "## TC-BAR-001: First Task\n"
            "**Status:** CLOSED\n\n"
            "## TC-BAR-002: Second Task\n"
            "**Status:** OPEN\n"
        )
        result = parse_plan_taskcards(plan)
        assert len(result) == 2
        assert result[0] == {"tc_id": "TC-BAR-001", "status": "CLOSED"}
        assert result[1] == {"tc_id": "TC-BAR-002", "status": "OPEN"}

    def test_inline_format(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text(
            "TC-INL-001 \u2014 **CLOSED**\n"
            "TC-INL-002: OPEN\n",
            encoding="utf-8",
        )
        result = parse_plan_taskcards(plan)
        assert len(result) == 2
        assert result[0] == {"tc_id": "TC-INL-001", "status": "CLOSED"}
        assert result[1] == {"tc_id": "TC-INL-002", "status": "OPEN"}

    def test_nonexistent_file(self):
        result = parse_plan_taskcards("/nonexistent/plan.md")
        assert result == []

    def test_no_taskcards(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text("# Empty Plan\nNo taskcards here.\n")
        result = parse_plan_taskcards(plan)
        assert result == []

    def test_mixed_statuses(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text(
            "| TC-MIX-001 | CLOSED | done |\n"
            "| TC-MIX-002 | SUPERSEDED | replaced |\n"
            "| TC-MIX-003 | EXCLUDED | not needed |\n"
            "| TC-MIX-004 | PENDING | todo |\n"
        )
        result = parse_plan_taskcards(plan)
        assert len(result) == 4
        closed_or_terminal = [tc for tc in result if tc["status"] in ("CLOSED", "SUPERSEDED", "EXCLUDED")]
        assert len(closed_or_terminal) == 3

    def test_table_priority_over_inline(self, tmp_path: Path):
        """If same TC appears in table and inline, table wins."""
        plan = tmp_path / "plan.md"
        plan.write_text(
            "| TC-DUP-001 | CLOSED | table says closed |\n"
            "TC-DUP-001 — OPEN\n"
        )
        result = parse_plan_taskcards(plan)
        assert len(result) == 1
        assert result[0]["status"] == "CLOSED"


class TestComputePlanHash:
    def test_hash_is_deterministic(self, tmp_path: Path):
        plan = tmp_path / "plan.md"
        plan.write_text("# Test Plan\n")
        h1 = compute_plan_hash(plan)
        h2 = compute_plan_hash(plan)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_hash_empty_on_nonexistent(self):
        assert compute_plan_hash("/nonexistent.md") == ""


# ---------------------------------------------------------------------------
# Lifecycle audit with plan-path tests (TC-TCF-003, TC-TCF-006)
# ---------------------------------------------------------------------------


class TestLifecycleAuditWithPlanPath:
    """Tests that lifecycle audit correctly uses plan_path to detect open taskcards."""

    def test_open_taskcard_blocks_audit_pass(self, tmp_path: Path):
        """Pilot B: Open requirement blocks closure."""
        plan = tmp_path / "plan.md"
        plan.write_text("| TC-TEST-001 | CLOSED | done |\n| TC-TEST-002 | OPEN | todo |\n")

        # Create minimal signal file for audit
        signal_dir = tmp_path / ".local" / "supervisor"
        signal_dir.mkdir(parents=True)
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": [],
        }))

        result = run_lifecycle_audit(repo_root=tmp_path, plan_path=plan)
        assert result["verdict"] == "AUDIT_REQUIRES_ITERATION"
        assert any(tc["tc_id"] == "TC-TEST-002" for tc in result["open_taskcards"])
        assert result["all_taskcards_closed"] is False
        assert result["mission_complete"] is False

    def test_all_closed_allows_audit_pass(self, tmp_path: Path):
        """Pilot A: Fully complete plan allows closure."""
        plan = tmp_path / "plan.md"
        plan.write_text("| TC-TEST-001 | CLOSED | done |\n| TC-TEST-002 | CLOSED | done |\n")

        signal_dir = tmp_path / ".local" / "supervisor"
        signal_dir.mkdir(parents=True)
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": [],
        }))

        result = run_lifecycle_audit(repo_root=tmp_path, plan_path=plan)
        assert result["verdict"] == "AUDIT_PASS"
        assert result["open_taskcards"] == []
        assert result["all_taskcards_closed"] is True
        assert result["mission_complete"] is True

    def test_no_plan_path_preserves_old_behavior(self, tmp_path: Path):
        """Without plan_path, audit checks only signal/evidence state."""
        signal_dir = tmp_path / ".local" / "supervisor"
        signal_dir.mkdir(parents=True)
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": [],
        }))

        result = run_lifecycle_audit(repo_root=tmp_path)
        assert result["verdict"] == "AUDIT_PASS"
        assert result["open_taskcards"] == []
        assert result["total_taskcards_parsed"] == 0

    def test_empty_taskcards_is_conservative(self, tmp_path: Path):
        """Plan with no parseable taskcards: all_taskcards_closed=False (conservative)."""
        plan = tmp_path / "plan.md"
        plan.write_text("# Plan\nNo structured taskcards.\n")

        signal_dir = tmp_path / ".local" / "supervisor"
        signal_dir.mkdir(parents=True)
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": [],
        }))

        result = run_lifecycle_audit(repo_root=tmp_path, plan_path=plan)
        assert result["total_taskcards_parsed"] == 0
        assert result["all_taskcards_closed"] is False  # Conservative: no TCs found = not proven closed


# ---------------------------------------------------------------------------
# Closure contract tests (TC-TCF-006)
# ---------------------------------------------------------------------------


class TestClosureContract:
    def test_all_true_authorizes(self):
        audit_result = {
            "findings": [],
            "open_taskcards": [],
            "all_taskcards_closed": True,
            "rework_items": [],
            "open_gaps": [],
            "mission_complete": True,
        }
        contract = build_closure_contract(audit_result, plan_path="test.md")
        assert contract["closure_authorized"] is True
        assert contract["all_mandatory_tasks_closed"] is True

    def test_open_taskcard_blocks(self):
        audit_result = {
            "findings": [{"type": "OPEN_TASKCARD", "severity": "CRITICAL"}],
            "open_taskcards": [{"tc_id": "TC-X-001", "status": "OPEN"}],
            "all_taskcards_closed": False,
            "rework_items": [],
            "open_gaps": [],
            "mission_complete": False,
        }
        contract = build_closure_contract(audit_result, plan_path="test.md")
        assert contract["closure_authorized"] is False
        assert contract["all_mandatory_tasks_closed"] is False

    def test_govblock_blocks(self):
        audit_result = {
            "findings": [{"type": "GOVBLOCK_PRESENT", "severity": "CRITICAL"}],
            "open_taskcards": [],
            "all_taskcards_closed": True,
            "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
            "open_gaps": [],
            "mission_complete": False,
        }
        contract = build_closure_contract(audit_result, plan_path="test.md")
        assert contract["closure_authorized"] is False
        assert contract["no_govblock_unresolved"] is False

    def test_advisory_rework_does_not_block(self):
        audit_result = {
            "findings": [],
            "open_taskcards": [],
            "all_taskcards_closed": True,
            "rework_items": ["LANE_ENFORCEMENT:1_violations"],
            "open_gaps": [],
            "mission_complete": True,
        }
        contract = build_closure_contract(audit_result, plan_path="test.md")
        assert contract["closure_authorized"] is True
        assert contract["all_rework_closed"] is False  # Has items, but non-GOV_BLOCK


# ---------------------------------------------------------------------------
# Error fallback tests (TC-TCF-004 — D6 fix)
# ---------------------------------------------------------------------------


class TestErrorFallbackSafety:
    """Verify that audit errors produce ITERATION_REQUIRED, not TERMINAL_CLOSED."""

    def test_import_error_fallback(self, tmp_path: Path):
        """When lifecycle_audit can't be imported, fallback must be ITERATION_REQUIRED."""
        sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))
        from write_plan_lock import write_lock

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared_lock = tmp_path / "active-plan-lock.json"

        import write_plan_lock as wpl
        orig_shared = wpl._shared_lock_path
        orig_dir = wpl._plan_locks_dir
        try:
            wpl._shared_lock_path = shared_lock
            wpl._plan_locks_dir = lock_dir

            # Mock only the lifecycle_audit import to raise ImportError
            real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

            def selective_import(name, *args, **kwargs):
                if name == "lifecycle_audit":
                    raise ImportError("test: module not found")
                return real_import(name, *args, **kwargs)

            with mock.patch.dict(sys.modules, {"lifecycle_audit": None}):
                with mock.patch("builtins.__import__", side_effect=selective_import):
                    write_lock(
                        "test-plan.md",
                        terminal=True,
                        audit_gate=True,
                        session_id="test-err",
                    )

            lock = json.loads(shared_lock.read_text())
            assert lock["status"] == "ITERATION_REQUIRED", \
                f"Expected ITERATION_REQUIRED on ImportError, got {lock['status']}"
        finally:
            wpl._shared_lock_path = orig_shared
            wpl._plan_locks_dir = orig_dir

    def test_exception_fallback(self, tmp_path: Path):
        """When lifecycle_audit raises, fallback must be ITERATION_REQUIRED."""
        sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))
        from write_plan_lock import write_lock

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared_lock = tmp_path / "active-plan-lock.json"

        import write_plan_lock as wpl
        orig_shared = wpl._shared_lock_path
        orig_dir = wpl._plan_locks_dir
        try:
            wpl._shared_lock_path = shared_lock
            wpl._plan_locks_dir = lock_dir

            # Create a mock module that raises on run_lifecycle_audit
            mock_module = mock.MagicMock()
            mock_module.run_lifecycle_audit.side_effect = RuntimeError("test crash")

            with mock.patch.dict(sys.modules, {"lifecycle_audit": mock_module}):
                write_lock(
                    "test-plan.md",
                    terminal=True,
                    audit_gate=True,
                    session_id="test-exc",
                )

            lock = json.loads(shared_lock.read_text())
            assert lock["status"] == "ITERATION_REQUIRED", \
                f"Expected ITERATION_REQUIRED on Exception, got {lock['status']}"
        finally:
            wpl._shared_lock_path = orig_shared
            wpl._plan_locks_dir = orig_dir


def _mock_import_error(name, *args, **kwargs):
    if name == "lifecycle_audit":
        raise ImportError("test: module not found")
    return __builtins__.__import__(name, *args, **kwargs) if hasattr(__builtins__, '__import__') else None


# ---------------------------------------------------------------------------
# COMPLETION_CANDIDATE tests (TC-TCF-005)
# ---------------------------------------------------------------------------


class TestCompletionCandidate:
    def test_completion_candidate_does_not_block(self, tmp_path: Path):
        """COMPLETION_CANDIDATE status must return CONTINUE from check_continuation."""
        from check_continuation import check

        # Write COMPLETION_CANDIDATE lock
        lock_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
        lock_dir.mkdir(parents=True)
        lock = {
            "plan_path": "test.md",
            "status": "COMPLETION_CANDIDATE",
            "last_taskcard": None,
            "session_id": "test-cc",
            "track_type": "product",
            "updated_at": "2026-06-23T17:00:00Z",
        }
        (lock_dir / "test-cc.json").write_text(json.dumps(lock))
        (tmp_path / ".local" / "supervisor" / "active-plan-lock.json").write_text(json.dumps(lock))

        # Write signal
        (tmp_path / ".local" / "supervisor" / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "iteration": 0,
            "max_iterations": 5,
        }))

        result = check(tmp_path, session_id="test-cc")
        assert result["verdict"] == "CONTINUE"
        assert result.get("completion_candidate_detected") is True


# ---------------------------------------------------------------------------
# Reopening tests (TC-TCF-007)
# ---------------------------------------------------------------------------


class TestReopenPlanLock:
    def test_reopen_transitions_to_in_progress(self, tmp_path: Path):
        """Pilot H: Missed work reopens same plan."""
        from reopen_plan_lock import reopen_plan, _plan_locks_dir, _shared_lock_path, _reopening_register_path
        import reopen_plan_lock as rpl

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared = tmp_path / "active-plan-lock.json"
        register = tmp_path / "reopening-register.json"

        orig_dir, orig_shared, orig_reg = rpl._plan_locks_dir, rpl._shared_lock_path, rpl._reopening_register_path
        try:
            rpl._plan_locks_dir = lock_dir
            rpl._shared_lock_path = shared
            rpl._reopening_register_path = register

            lock = {
                "plan_path": "test-plan.md",
                "status": "TERMINAL_CLOSED",
                "session_id": "old-session",
                "updated_at": "2026-06-23T12:00:00Z",
                "track_type": "product",
            }
            (lock_dir / "old-session.json").write_text(json.dumps(lock))
            shared.write_text(json.dumps(lock))

            record = reopen_plan(
                plan_path="test-plan.md",
                reason="Missed TC-XXX",
                trigger="MISSED_REQUIREMENT",
            )

            # Verify old lock marked SUPERSEDED (new lock created separately by write_lock)
            updated = json.loads((lock_dir / "old-session.json").read_text())
            assert updated["status"] == "SUPERSEDED"
            assert len(updated.get("closure_history", [])) == 1
            assert updated["closure_history"][0]["status"] == "TERMINAL_CLOSED"

            # Verify register entry
            reg = json.loads(register.read_text())
            assert len(reg) == 1
            assert reg[0]["trigger"] == "MISSED_REQUIREMENT"
            assert record["prior_closure_preserved"] is True
        finally:
            rpl._plan_locks_dir = orig_dir
            rpl._shared_lock_path = orig_shared
            rpl._reopening_register_path = orig_reg

    def test_reopen_requires_terminal_or_complete(self, tmp_path: Path):
        """Cannot reopen a plan that is IN_PROGRESS."""
        import reopen_plan_lock as rpl

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared = tmp_path / "active.json"

        orig_dir, orig_shared = rpl._plan_locks_dir, rpl._shared_lock_path
        try:
            rpl._plan_locks_dir = lock_dir
            rpl._shared_lock_path = shared

            lock = {"plan_path": "test.md", "status": "IN_PROGRESS", "session_id": "s1"}
            (lock_dir / "s1.json").write_text(json.dumps(lock))
            shared.write_text(json.dumps(lock))

            with pytest.raises(ValueError, match="Cannot reopen"):
                from reopen_plan_lock import reopen_plan
                reopen_plan("test.md", reason="test", trigger="OTHER")
        finally:
            rpl._plan_locks_dir = orig_dir
            rpl._shared_lock_path = orig_shared

    def test_successor_mode_marks_superseded(self, tmp_path: Path):
        """Pilot I: Out-of-scope work creates successor."""
        import reopen_plan_lock as rpl

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared = tmp_path / "active.json"
        register = tmp_path / "register.json"

        orig_dir, orig_shared, orig_reg = rpl._plan_locks_dir, rpl._shared_lock_path, rpl._reopening_register_path
        try:
            rpl._plan_locks_dir = lock_dir
            rpl._shared_lock_path = shared
            rpl._reopening_register_path = register

            lock = {"plan_path": "old-plan.md", "status": "TERMINAL_CLOSED", "session_id": "s1",
                    "updated_at": "2026-06-23T12:00:00Z", "track_type": "product"}
            (lock_dir / "s1.json").write_text(json.dumps(lock))
            shared.write_text(json.dumps(lock))

            from reopen_plan_lock import reopen_plan
            record = reopen_plan(
                plan_path="old-plan.md",
                reason="New out-of-scope feature",
                trigger="OUT_OF_SCOPE_WORK",
                successor_path="new-plan.md",
            )

            updated = json.loads((lock_dir / "s1.json").read_text())
            assert updated["status"] == "SUPERSEDED"  # Old lock always marked SUPERSEDED
            assert updated.get("successor_plan_path") == "new-plan.md"
            assert record["new_status"] == "SUPERSEDED_BY_SUCCESSOR"  # Record tracks intent
        finally:
            rpl._plan_locks_dir = orig_dir
            rpl._shared_lock_path = orig_shared
            rpl._reopening_register_path = orig_reg

    def test_idempotent_reopen(self, tmp_path: Path):
        """Pilot L: Second reopen attempt does not create duplicate register entry."""
        import reopen_plan_lock as rpl

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared = tmp_path / "active.json"
        register = tmp_path / "register.json"

        orig_dir, orig_shared, orig_reg = rpl._plan_locks_dir, rpl._shared_lock_path, rpl._reopening_register_path
        try:
            rpl._plan_locks_dir = lock_dir
            rpl._shared_lock_path = shared
            rpl._reopening_register_path = register

            lock = {"plan_path": "test.md", "status": "TERMINAL_CLOSED", "session_id": "s1",
                    "updated_at": "2026-06-23T12:00:00Z", "track_type": "product"}

            # First reopen
            (lock_dir / "s1.json").write_text(json.dumps(lock))
            shared.write_text(json.dumps(lock))
            from reopen_plan_lock import reopen_plan
            reopen_plan("test.md", reason="first", trigger="MISSED_REQUIREMENT")

            # Manually reset to TERMINAL_CLOSED for second attempt
            lock2 = json.loads((lock_dir / "s1.json").read_text())
            lock2["status"] = "TERMINAL_CLOSED"
            (lock_dir / "s1.json").write_text(json.dumps(lock2))
            shared.write_text(json.dumps(lock2))

            reopen_plan("test.md", reason="first", trigger="MISSED_REQUIREMENT")

            reg = json.loads(register.read_text())
            assert len(reg) == 1  # Still just 1 entry (idempotent)
        finally:
            rpl._plan_locks_dir = orig_dir
            rpl._shared_lock_path = orig_shared
            rpl._reopening_register_path = orig_reg


# ---------------------------------------------------------------------------
# Negative controls
# ---------------------------------------------------------------------------


class TestNegativeControls:
    def test_terminal_without_audit_gate_still_closes(self, tmp_path: Path):
        """Negative: --terminal without --audit-gate should still close (with warning)."""
        sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))
        from write_plan_lock import write_lock
        import write_plan_lock as wpl

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared_lock = tmp_path / "active.json"
        orig_shared, orig_dir = wpl._shared_lock_path, wpl._plan_locks_dir
        try:
            wpl._shared_lock_path = shared_lock
            wpl._plan_locks_dir = lock_dir
            write_lock("test.md", terminal=True, session_id="neg-1")
            lock = json.loads(shared_lock.read_text())
            assert lock["status"] == "TERMINAL_CLOSED"  # Still closes (backward compat)
        finally:
            wpl._shared_lock_path = orig_shared
            wpl._plan_locks_dir = orig_dir

    def test_rework_items_block_closure(self, tmp_path: Path):
        """GOV_BLOCK rework items prevent AUDIT_PASS."""
        signal_dir = tmp_path / ".local" / "supervisor"
        signal_dir.mkdir(parents=True)
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": ["GOV_BLOCK:monolith_detection_validator"],
        }))

        result = run_lifecycle_audit(repo_root=tmp_path)
        assert result["verdict"] == "AUDIT_REQUIRES_ITERATION"


# ---------------------------------------------------------------------------
# Integration tests — convergence hardening (F1-F3)
# ---------------------------------------------------------------------------


class TestReopenPlanLockIntegration:
    """F3: Test reopen_plan_lock against realistic lock directory structure."""

    def test_reopen_real_lock_structure(self, tmp_path: Path):
        """Create a TERMINAL_CLOSED lock in plan-locks/, reopen it, verify IN_PROGRESS."""
        import reopen_plan_lock as rpl

        plan_file = tmp_path / "plans" / "test-plan.md"
        plan_file.parent.mkdir(parents=True)
        plan_file.write_text(
            "# Test Plan\n"
            "| TC-INT-001 | OPEN | Integration test |\n"
        )

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared = tmp_path / "active.json"
        register = tmp_path / "register.json"

        session_lock = lock_dir / "test-session.json"
        session_lock.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
            "session_id": "test-session",
            "updated_at": "2026-06-23T00:00:00Z",
        }))
        shared.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
        }))

        orig_dir = rpl._plan_locks_dir
        orig_shared = rpl._shared_lock_path
        orig_reg = rpl._reopening_register_path
        try:
            rpl._plan_locks_dir = lock_dir
            rpl._shared_lock_path = shared
            rpl._reopening_register_path = register

            result = rpl.reopen_plan(
                plan_path=str(plan_file),
                reason="Integration test reopening",
                trigger="AUDIT_FINDING",
            )
            # reopen_plan returns the reopening record, not a status dict
            assert result["trigger"] == "AUDIT_FINDING"
            assert result["prior_closure_preserved"] is True

            # Verify the old lock was marked SUPERSEDED (new lock created separately)
            updated_lock = json.loads(session_lock.read_text())
            assert updated_lock["status"] == "SUPERSEDED"
            assert "closure_history" in updated_lock
            assert len(updated_lock["closure_history"]) == 1
        finally:
            rpl._plan_locks_dir = orig_dir
            rpl._shared_lock_path = orig_shared
            rpl._reopening_register_path = orig_reg

    def test_reopen_then_lifecycle_audit(self, tmp_path: Path):
        """After reopening, lifecycle audit should detect open taskcards and block."""
        import reopen_plan_lock as rpl

        plan_file = tmp_path / "plans" / "audit-plan.md"
        plan_file.parent.mkdir(parents=True)
        plan_file.write_text(
            "# Audit Plan\n"
            "| TC-AUD-001 | OPEN | Still open |\n"
            "| TC-AUD-002 | CLOSED | Done |\n",
            encoding="utf-8",
        )

        lock_dir = tmp_path / "plan-locks"
        lock_dir.mkdir(parents=True)
        shared = tmp_path / "active.json"
        register = tmp_path / "register.json"

        session_lock = lock_dir / "audit-session.json"
        session_lock.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
            "session_id": "audit-session",
        }))
        shared.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
        }))

        orig_dir = rpl._plan_locks_dir
        orig_shared = rpl._shared_lock_path
        orig_reg = rpl._reopening_register_path
        try:
            rpl._plan_locks_dir = lock_dir
            rpl._shared_lock_path = shared
            rpl._reopening_register_path = register

            rpl.reopen_plan(
                plan_path=str(plan_file),
                reason="Open taskcards remain",
                trigger="AUDIT_FINDING",
            )
        finally:
            rpl._plan_locks_dir = orig_dir
            rpl._shared_lock_path = orig_shared
            rpl._reopening_register_path = orig_reg

        # Lifecycle audit should block because TC-AUD-001 is OPEN
        signal_dir = tmp_path / ".local" / "supervisor"
        signal_dir.mkdir(parents=True)
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": [],
        }))

        result = run_lifecycle_audit(
            repo_root=tmp_path,
            plan_path=str(plan_file),
        )
        assert result["all_taskcards_closed"] is False
        assert len(result["open_taskcards"]) == 1
        assert result["open_taskcards"][0]["tc_id"] == "TC-AUD-001"
        assert result["verdict"] == "AUDIT_REQUIRES_ITERATION"


class TestCompletionCandidateIntegration:
    """F2: Test COMPLETION_CANDIDATE → check_continuation returns CONTINUE."""

    def test_completion_candidate_check_continuation(self, tmp_path: Path):
        """Write COMPLETION_CANDIDATE lock, verify check_continuation returns CONTINUE."""
        from check_continuation import check  # type: ignore[import]

        lock_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
        lock_dir.mkdir(parents=True)

        session_id = "cc-test-session"
        session_lock = lock_dir / f"{session_id}.json"
        session_lock.write_text(json.dumps({
            "plan_path": "plans/test-cc.md",
            "status": "COMPLETION_CANDIDATE",
            "session_id": session_id,
            "updated_at": "2026-06-23T00:00:00Z",
        }))

        # Write session ID file
        sid_file = tmp_path / ".local" / "supervisor" / f"session-product.id"
        sid_file.write_text(json.dumps({"session_id": session_id}))

        # Write continuation signal
        signal_file = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
        signal_file.write_text(json.dumps({
            "autonomous_continue": True,
            "iteration": 0,
            "max_iterations": 10,
            "session_id": session_id,
        }))

        result = check(tmp_path, session_id=session_id)
        assert result["verdict"] == "CONTINUE"
        assert result.get("completion_candidate_detected") is True


class TestAutonomousReopenDetection:
    """F1: Test Step 0b-reopen-check logic from autonomous_cycle."""

    def test_detect_terminal_with_open_taskcards(self, tmp_path: Path):
        """Simulate what Step 0b does: find TERMINAL_CLOSED plan with open TCs."""
        # This tests the detection logic directly (not through autonomous_cycle.py)
        plan_file = tmp_path / "plans" / "reopen-detect.md"
        plan_file.parent.mkdir(parents=True)
        plan_file.write_text(
            "# Detect Plan\n"
            "| TC-DET-001 | OPEN | Still open |\n"
            "| TC-DET-002 | CLOSED | Done |\n",
            encoding="utf-8",
        )

        lock_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
        lock_dir.mkdir(parents=True)
        lock_file = lock_dir / "detect-session.json"
        lock_file.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
            "session_id": "detect-session",
        }))

        # Simulate the Step 0b detection logic
        should_reopen = False
        for lf in lock_dir.glob("*.json"):
            lock = json.loads(lf.read_text())
            if lock.get("status") != "TERMINAL_CLOSED":
                continue
            plan_path = lock.get("plan_path", "")
            if not plan_path or not Path(plan_path).exists():
                continue
            tcs = parse_plan_taskcards(plan_path)
            open_tcs = [tc for tc in tcs if tc["status"] not in ("CLOSED", "SUPERSEDED", "EXCLUDED")]
            if open_tcs:
                should_reopen = True

        assert should_reopen is True

    def test_no_reopen_when_all_closed(self, tmp_path: Path):
        """All taskcards CLOSED → no reopening needed."""
        plan_file = tmp_path / "plans" / "closed-plan.md"
        plan_file.parent.mkdir(parents=True)
        plan_file.write_text(
            "# Closed Plan\n"
            "| TC-CL-001 | CLOSED | Done |\n"
            "| TC-CL-002 | CLOSED | Also done |\n",
            encoding="utf-8",
        )

        lock_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
        lock_dir.mkdir(parents=True)
        lock_file = lock_dir / "closed-session.json"
        lock_file.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
            "session_id": "closed-session",
        }))

        should_reopen = False
        for lf in lock_dir.glob("*.json"):
            lock = json.loads(lf.read_text())
            if lock.get("status") != "TERMINAL_CLOSED":
                continue
            plan_path = lock.get("plan_path", "")
            if not plan_path or not Path(plan_path).exists():
                continue
            tcs = parse_plan_taskcards(plan_path)
            open_tcs = [tc for tc in tcs if tc["status"] not in ("CLOSED", "SUPERSEDED", "EXCLUDED")]
            if open_tcs:
                should_reopen = True

        assert should_reopen is False

    def test_full_detect_audit_cycle(self, tmp_path: Path):
        """F1 E2E: detect open TCs in TERMINAL_CLOSED → audit confirms block → contract unauthorized."""
        plan_file = tmp_path / "plans" / "e2e-plan.md"
        plan_file.parent.mkdir(parents=True)
        plan_file.write_text(
            "# E2E Plan\n"
            "| TC-E2E-001 | OPEN | Still open |\n"
            "| TC-E2E-002 | CLOSED | Done |\n",
            encoding="utf-8",
        )

        lock_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
        lock_dir.mkdir(parents=True)
        lock_file = lock_dir / "e2e-session.json"
        lock_file.write_text(json.dumps({
            "plan_path": str(plan_file),
            "status": "TERMINAL_CLOSED",
            "session_id": "e2e-session",
        }))

        # Step 1: Detect open taskcards (simulating Step 0b)
        tcs = parse_plan_taskcards(plan_file)
        open_tcs = [tc for tc in tcs if tc["status"] not in ("CLOSED", "SUPERSEDED", "EXCLUDED")]
        assert len(open_tcs) == 1
        assert open_tcs[0]["tc_id"] == "TC-E2E-001"

        # Step 2: Lifecycle audit with plan_path confirms open taskcards block
        signal_dir = tmp_path / ".local" / "supervisor"
        (signal_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": True,
            "rework_items": [],
        }))

        audit = run_lifecycle_audit(
            repo_root=tmp_path,
            plan_path=str(plan_file),
        )
        assert audit["all_taskcards_closed"] is False
        assert audit["verdict"] == "AUDIT_REQUIRES_ITERATION"
        assert audit["closure_contract"]["closure_authorized"] is False
        assert audit["total_taskcards_parsed"] == 2
        assert len(audit["open_taskcards"]) == 1
