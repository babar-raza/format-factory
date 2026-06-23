"""Regression tests for TC-HARD-002: stream field missing from PLAN_LOCKED return dict.

Root cause: generate_next_work_items() returned a PLAN_LOCKED dict without a "stream" field.
validate_next_work_items() stream_field_match check: `work_items.get("stream", "") == target_stream`
With no stream field: "" != "mainstream" → stream_field_match=False → autonomous_continue=False.

Fix (2026-06-22): Added "stream": stream or "mainstream" to the PLAN_LOCKED return dict
in generate_next_worker_prompt.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _make_active_plan_lock(plan_path: str = "C:/plans/test-plan.md",
                           status: str = "IN_PROGRESS") -> dict:
    return {
        "plan_path": plan_path,
        "status": status,
        "last_taskcard": "TC-TEST-001",
    }


def _make_minimal_review() -> dict:
    return {
        "run_id": "test-hard-002",
        "sprint_id": "TEST-HARD-002",
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


class TestStreamFieldPlanLocked:
    """TC-HARD-002: PLAN_LOCKED dict must include stream field for validate_next_work_items."""

    def test_plan_locked_dict_has_stream_field(self):
        """PLAN_LOCKED return dict must include a 'stream' key."""
        from generate_next_worker_prompt import generate_next_work_items
        plan_lock = _make_active_plan_lock()
        result = generate_next_work_items(_make_minimal_review(), stream="mainstream",
                                          plan_lock=plan_lock)
        assert result.get("work_selection_mode") == "PLAN_LOCKED", (
            "Expected PLAN_LOCKED mode when plan_lock is active"
        )
        assert "stream" in result, (
            f"PLAN_LOCKED dict missing 'stream' field. Keys: {list(result.keys())}"
        )

    def test_plan_locked_stream_matches_mainstream(self):
        """PLAN_LOCKED dict with stream=mainstream must equal 'mainstream'."""
        from generate_next_worker_prompt import generate_next_work_items
        plan_lock = _make_active_plan_lock()
        result = generate_next_work_items(_make_minimal_review(), stream="mainstream",
                                          plan_lock=plan_lock)
        assert result["stream"] == "mainstream", (
            f"Expected stream='mainstream', got {result.get('stream')!r}"
        )

    def test_plan_locked_stream_defaults_to_mainstream_when_no_stream_arg(self):
        """PLAN_LOCKED dict must default stream to 'mainstream' when stream=None."""
        from generate_next_worker_prompt import generate_next_work_items
        plan_lock = _make_active_plan_lock()
        result = generate_next_work_items(_make_minimal_review(), stream=None,
                                          plan_lock=plan_lock)
        assert result.get("stream") == "mainstream", (
            f"Expected 'mainstream' default, got {result.get('stream')!r}"
        )

    def test_plan_locked_stream_field_match_passes_validate(self):
        """validate_next_work_items must pass stream_field_match for PLAN_LOCKED mainstream."""
        from generate_next_worker_prompt import generate_next_work_items
        from validate_prompt_quality import validate_next_work_items
        plan_lock = _make_active_plan_lock()
        work_items = generate_next_work_items(_make_minimal_review(), stream="mainstream",
                                              plan_lock=plan_lock)
        result = validate_next_work_items(work_items, target_stream="mainstream")
        checks_by_name = {c["check"]: c for c in result.get("checks", [])}
        stream_check = checks_by_name.get("stream_field_match")
        assert stream_check is not None, "stream_field_match check not found in validation result"
        assert stream_check["pass"] is True, (
            f"stream_field_match should be True but got False. "
            f"detail={stream_check.get('detail')}"
        )

    def test_plan_locked_not_triggered_when_status_complete(self):
        """When plan_lock status=COMPLETE, system ledger is NOT suppressed."""
        from generate_next_worker_prompt import generate_next_work_items
        plan_lock = _make_active_plan_lock(status="COMPLETE")
        result = generate_next_work_items(_make_minimal_review(), stream="mainstream",
                                          plan_lock=plan_lock)
        # With status=COMPLETE, the plan lock guard does NOT fire — normal items are generated
        assert result.get("work_selection_mode") != "PLAN_LOCKED", (
            "PLAN_LOCKED should not activate when plan_lock.status=COMPLETE"
        )

    def test_plan_locked_stream_propagated_non_mainstream(self):
        """Non-mainstream streams are propagated to the PLAN_LOCKED dict."""
        from generate_next_worker_prompt import generate_next_work_items
        plan_lock = _make_active_plan_lock()
        result = generate_next_work_items(_make_minimal_review(), stream="supervisor",
                                          plan_lock=plan_lock)
        assert result.get("stream") == "supervisor", (
            f"Expected stream='supervisor' propagated, got {result.get('stream')!r}"
        )
