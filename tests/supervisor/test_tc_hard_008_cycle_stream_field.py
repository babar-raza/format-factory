"""Regression tests for TC-HARD-008: cycle-level stream_field_match confirmation.

Context:
  TC-HARD-002 added 'stream' field to the PLAN_LOCKED return dict in
  generate_next_work_items() (generate_next_worker_prompt.py line 994).
  TC-HARD-008 confirms that this fix prevents stream_field_match=False from
  blocking autonomous_continue when a plan lock is IN_PROGRESS.

Architectural note (structural catch-22):
  Running a full autonomous_cycle with an IN_PROGRESS plan lock is not feasible in
  a normal sprint test without overwriting live state. These tests instead verify
  the critical E2E path at the function boundary:
    generate_next_work_items(IN_PROGRESS lock) → validate_next_work_items() → stream_field_match=True

  This is the same execution path that autonomous_cycle.py traverses internally.
  The continuation-signal.json field 'stream_field_match' does NOT exist in the
  signal dict — it is an internal check inside validate_next_work_items() that
  influences whether autonomous_continue is written as True or False.

Proof level: PROOF_LEVEL_3 (function-level E2E, not full pipeline run).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _make_plan_lock(status: str = "IN_PROGRESS") -> dict:
    return {
        "plan_path": "C:/plans/tc-hard-008-test-plan.md",
        "status": status,
        "last_taskcard": "TC-TEST-001",
    }


def _make_review(**kwargs) -> dict:
    base = {
        "run_id": "tc-hard-008",
        "sprint_id": "TEST-TC-HARD-008",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "item_grades": [],
        "accepted_items": [],
        "rework_items": [],
        "rejected_items": [],
        "overclaimed_items": [],
        "evidence_quality_score": 1.0,
        "verified_item_count": 0,
        "test_results": {"passed": 0, "failed": 0, "skipped": 0},
    }
    base.update(kwargs)
    return base


class TestCycleStreamFieldPlanLocked:
    """TC-HARD-008: PLAN_LOCKED with IN_PROGRESS lock must pass stream_field_match."""

    def test_plan_locked_generates_stream_field(self):
        """generate_next_work_items with IN_PROGRESS lock emits stream field."""
        from generate_next_worker_prompt import generate_next_work_items
        result = generate_next_work_items(_make_review(), stream="mainstream",
                                          plan_lock=_make_plan_lock("IN_PROGRESS"))
        assert result.get("work_selection_mode") == "PLAN_LOCKED"
        assert "stream" in result, f"Missing stream field. Keys: {list(result.keys())}"
        assert result["stream"] == "mainstream"

    def test_stream_field_match_passes_for_plan_locked(self):
        """validate_next_work_items: stream_field_match=True when PLAN_LOCKED with stream."""
        from generate_next_worker_prompt import generate_next_work_items
        from validate_prompt_quality import validate_next_work_items
        work_items = generate_next_work_items(_make_review(), stream="mainstream",
                                              plan_lock=_make_plan_lock("IN_PROGRESS"))
        result = validate_next_work_items(work_items, target_stream="mainstream")
        checks = {c["check"]: c for c in result.get("checks", [])}
        sfm = checks.get("stream_field_match")
        assert sfm is not None, "stream_field_match check absent from validation result"
        assert sfm["pass"] is True, (
            f"stream_field_match should be True but was False. detail={sfm.get('detail')}"
        )

    def test_overall_validation_passes_for_plan_locked(self):
        """All validate_next_work_items checks pass for PLAN_LOCKED mainstream."""
        from generate_next_worker_prompt import generate_next_work_items
        from validate_prompt_quality import validate_next_work_items
        work_items = generate_next_work_items(_make_review(), stream="mainstream",
                                              plan_lock=_make_plan_lock("IN_PROGRESS"))
        result = validate_next_work_items(work_items, target_stream="mainstream")
        failing = [c for c in result.get("checks", []) if not c.get("pass", True)]
        assert not failing, (
            f"Unexpected validation failures: {[c['check'] for c in failing]}"
        )

    def test_autonomous_continue_would_be_true_for_plan_locked(self):
        """Simulation: autonomous_continue would not be set to False by stream_field_match failure."""
        from generate_next_worker_prompt import generate_next_work_items
        from validate_prompt_quality import validate_next_work_items
        work_items = generate_next_work_items(_make_review(), stream="mainstream",
                                              plan_lock=_make_plan_lock("IN_PROGRESS"))
        result = validate_next_work_items(work_items, target_stream="mainstream")
        # The autonomous_cycle uses: if not all checks pass → set autonomous_continue=False
        all_pass = all(c.get("pass", True) for c in result.get("checks", []))
        assert all_pass, "Validation failure would cause autonomous_continue=False"

    def test_complete_plan_lock_does_not_trigger_plan_locked_mode(self):
        """COMPLETE plan lock must NOT activate PLAN_LOCKED mode (normal ledger work allowed)."""
        from generate_next_worker_prompt import generate_next_work_items
        result = generate_next_work_items(_make_review(), stream="mainstream",
                                          plan_lock=_make_plan_lock("COMPLETE"))
        assert result.get("work_selection_mode") != "PLAN_LOCKED", (
            "COMPLETE plan lock should not block ledger work"
        )

    def test_terminal_closed_does_not_block_stream_field_match(self):
        """TERMINAL_CLOSED plan lock produces valid output with stream field.

        TERMINAL_CLOSED may or may not trigger PLAN_LOCKED mode depending on the
        implementation version. The key invariant is that stream_field_match passes.
        """
        from generate_next_worker_prompt import generate_next_work_items
        from validate_prompt_quality import validate_next_work_items
        result = generate_next_work_items(_make_review(), stream="mainstream",
                                          plan_lock=_make_plan_lock("TERMINAL_CLOSED"))
        assert "stream" in result, "Missing stream field for TERMINAL_CLOSED case"
        val = validate_next_work_items(result, target_stream="mainstream")
        checks = {c["check"]: c for c in val.get("checks", [])}
        sfm = checks.get("stream_field_match", {})
        assert sfm.get("pass") is True, "stream_field_match should be True for TERMINAL_CLOSED case"

    def test_stream_field_detail_is_correct(self):
        """stream_field_match detail must show actual vs target stream values."""
        from generate_next_worker_prompt import generate_next_work_items
        from validate_prompt_quality import validate_next_work_items
        work_items = generate_next_work_items(_make_review(), stream="mainstream",
                                              plan_lock=_make_plan_lock("IN_PROGRESS"))
        result = validate_next_work_items(work_items, target_stream="mainstream")
        checks = {c["check"]: c for c in result.get("checks", [])}
        sfm = checks.get("stream_field_match", {})
        detail = sfm.get("detail", "")
        assert "mainstream" in detail, (
            f"Expected 'mainstream' in detail string, got: {detail!r}"
        )
