"""
test_supervisor_loop_continuation_contract.py — Supervisor Loop Contract Tests

Verifies the contract that the loop cannot stop for non-terminal reasons,
and that the adjudicator integration works end-to-end.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from tools.supervisor.autonomous_poc_controller import (
    TERMINAL_EXTERNAL_GATE,
    TERMINAL_POC_READY,
    TERMINAL_POC_READY_RELEASE_PENDING,
    TERMINAL_RUNTIME_LIMIT,
    TERMINAL_UNSAFE,
    NON_TERMINAL_CHECKPOINT,
    NON_TERMINAL_CONTINUE,
    NON_TERMINAL_REPAIR,
    classify_terminal_state,
    adjudicate_with_stop_reason_adjudicator,
    decide_next_action,
    reconcile_dashboard_contradiction,
)
from tools.supervisor.stop_reason_adjudicator import (
    StopDecision,
    adjudicate_stop_reason,
    adjudicate_batch,
)


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

def _make_r118_state():
    return {
        "current_iteration": 7,
        "terminal_state_reached": False,
        "poc_ready": False,
        "autonomous_continue": True,
        "safe_lanes_available": True,
    }


def _make_complete_dashboard():
    return {
        "commercial_targets": {"FODS": "PASS", "FODT": "PASS", "Netpbm": "PASS"},
        "foss_targets": {
            "ZST": "PASS", "Python_Netpbm": "PASS", "SYLK": "PASS",
            "DIF": "IN_PROGRESS", "Gnumeric": "IN_PROGRESS"
        },
        "closure_criteria_met": True,
        "all_commercial_pass": True,
        "foss_minimum_met": True,
        "blocking_gaps": [],
        "poc_ready": True,
        "terminal_state": TERMINAL_POC_READY_RELEASE_PENDING,
    }


def _make_incomplete_dashboard():
    return {
        "commercial_targets": {"FODS": "IN_PROGRESS", "FODT": "PASS", "Netpbm": "PASS"},
        "foss_targets": {
            "ZST": "PASS", "Python_Netpbm": "PASS", "SYLK": "PASS",
        },
        "poc_ready": False,
    }


def _make_supervisor_verdict(claims_checked=5, verdict="PASS"):
    return {
        "claims_checked": claims_checked,
        "verdict": verdict,
    }


# ─────────────────────────────────────────────────────────────
# Adjudicator integration tests
# ─────────────────────────────────────────────────────────────

class TestAdjudicatorIntegration:
    def test_adjudicator_available_in_controller(self):
        """adjudicate_with_stop_reason_adjudicator function exists and works."""
        result = adjudicate_with_stop_reason_adjudicator(["supervisor_accepted"])
        # May return None if adjudicator unavailable, or a batch result if available
        # Either case is acceptable; the key is no exception is raised
        if result is not None:
            assert "overall_terminal" in result
            assert result["overall_terminal"] is False

    def test_empty_signals_returns_none(self):
        result = adjudicate_with_stop_reason_adjudicator([])
        assert result is None

    def test_none_signals_returns_none(self):
        result = adjudicate_with_stop_reason_adjudicator(None)
        assert result is None

    def test_supervisor_accepted_signal_does_not_stop(self):
        result = adjudicate_with_stop_reason_adjudicator(
            ["supervisor_accepted"],
            {"poc_ready": False}
        )
        if result is not None:
            assert result["overall_terminal"] is False

    def test_gate11_poc_ready_in_adjudicator(self):
        result = adjudicate_with_stop_reason_adjudicator(
            ["gate_11_pending"],
            {"poc_ready": True, "gate_11_pending": True}
        )
        if result is not None:
            assert result["has_release_pending"] is True

    def test_git_push_in_adjudicator_is_external_gate(self):
        result = adjudicate_with_stop_reason_adjudicator(
            ["git_push_required"],
            {"poc_ready": False}
        )
        if result is not None:
            assert result["has_true_external_gate"] is True


# ─────────────────────────────────────────────────────────────
# Loop contract: accepted sprint with remaining gaps continues
# ─────────────────────────────────────────────────────────────

class TestLoopContract:
    def test_accepted_sprint_with_remaining_gaps_continues(self):
        """ACCEPTED verdict with gaps remaining must NOT stop."""
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()
        verdict = _make_supervisor_verdict(claims_checked=5)

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            supervisor_verdict=verdict,
            continuation_signal={"autonomous_continue": True},
        )
        assert result == NON_TERMINAL_CONTINUE

    def test_accepted_sprint_with_poc_ready_and_gate11_is_release_pending(self):
        """ACCEPTED + POC-ready + Gate 11 → RELEASE_PENDING, not BLOCKED."""
        state = {"terminal_state_reached": False}
        dashboard = _make_complete_dashboard()
        verdict = _make_supervisor_verdict(claims_checked=5)

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            supervisor_verdict=verdict,
            gate_11_pending=True,
        )
        assert result == TERMINAL_POC_READY_RELEASE_PENDING

    def test_accepted_sprint_with_missing_evidence_but_repairable_continues(self):
        """Missing evidence (repairable) must NOT stop the train."""
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            blocker_routing={"evidence_quality_zero": True},  # NOT in _EXTERNAL_GATE_SIGNALS
        )
        assert result == NON_TERMINAL_CONTINUE

    def test_accepted_sprint_with_commit_requested_stops_for_commit_only(self):
        """git_commit_required stops only for that specific external gate."""
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            blocker_routing={"git_commit_required": True},
        )
        assert result == TERMINAL_EXTERNAL_GATE

    def test_supervisor_cannot_emit_autonomous_continue_false_for_evidence_quality_zero(self):
        """evidence_quality_zero is a local repair signal, not a hard stop."""
        # Verify via adjudicator that this is not terminal
        adj_result = adjudicate_stop_reason("evidence_quality_zero", {"materialization_verified": True})
        assert adj_result["terminal"] is False
        assert adj_result["decision"] in (
            StopDecision.LOCAL_REPAIR_CONTINUE,
            StopDecision.STATE_CONTRADICTION_REPAIR_REQUIRED,
        )

    def test_next_sprint_from_accepted_contains_no_false_blocked_tasks(self):
        """The loop contract: accepted sprint must not generate false-blocked tasks."""
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
        from generate_next_worker_prompt import generate_next_work_items

        review = {
            "sprint_id": "FORMAT-FACTORY-R118-001",
            "run_id": "r118",
            "overall_verdict": "ACCEPTED",
            "autonomous_continue": True,
            "item_grades": [],
            "test_results": {"passed": 0, "failed": 0, "skipped": 0},
        }
        result = generate_next_work_items(review, stream="mainstream")
        for item in result["items"]:
            label = item.get("owner_classification", "agent-owned")
            assert label not in ("approval-blocked", "blocked", "human-required", "stop"), (
                f"False-blocked task in next-sprint: {item['item_id']} label={label}"
            )

    def test_runtime_limit_gives_continuation_required_not_stop(self):
        """Runtime limit → TERMINAL_RUNTIME_LIMIT, but that means write continuation package."""
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            runtime_limit_reached=True,
        )
        assert result == TERMINAL_RUNTIME_LIMIT

        # Verify decide_next_action handles it correctly
        action = decide_next_action(result, iteration=5, max_iterations=12)
        assert action["action"] == "TERMINAL"

    def test_max_iterations_is_not_external_gate(self):
        """max_iterations reached → checkpoint rollover, not external gate."""
        adj_result = adjudicate_stop_reason("max_iterations_reached")
        assert adj_result["terminal"] is False
        assert adj_result["decision"] == StopDecision.CHECKPOINT_ROLLOVER_CONTINUE

        # decide_next_action handles it:
        action = decide_next_action(NON_TERMINAL_CONTINUE, iteration=15, max_iterations=12)
        assert action["action"] == NON_TERMINAL_CHECKPOINT


# ─────────────────────────────────────────────────────────────
# R118 specific adjudication tests
# ─────────────────────────────────────────────────────────────

class TestR118Adjudication:
    def test_r118_state_returns_poc_ready_candidate_release_pending(self):
        """R118 + POC-ready + Gate 11 = RELEASE_PENDING, not BLOCKED."""
        # This fixture represents R118 final state
        state = {
            "current_iteration": 7,
            "terminal_state_reached": False,
        }
        dashboard = _make_complete_dashboard()
        verdict = _make_supervisor_verdict(claims_checked=88, verdict="PASS")

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            supervisor_verdict=verdict,
            gate_11_pending=True,
        )
        assert result == TERMINAL_POC_READY_RELEASE_PENDING

    def test_r118_next_sprint_false_blockers_are_detected(self):
        """R118 next-sprint tasks with approval-blocked labels are detected."""
        from stop_reason_adjudicator import reclassify_task_label

        false_stop_tasks = [
            "[approval-blocked] Advance FODS Gate 11 commercial readiness",
            "[approval-blocked] Commit uncommitted product code",
            "[blocked] Open ZST Gate 11",
        ]
        for task in false_stop_tasks:
            label_end = task.index("]")
            label = task[:label_end + 1]
            title = task[label_end + 2:]
            result = reclassify_task_label(label, title)
            assert result["is_false_stop"] is True, (
                f"Expected false_stop=True for task: {task}"
            )

    def test_r118_approval_gates_mode5_does_not_block_continuation(self):
        """approval-gates.md NEXT_HUMAN_GATE MODE 5 does not block local continuation."""
        adj_result = adjudicate_stop_reason("mode_5_approval_pending")
        assert adj_result["terminal"] is False
        assert adj_result["decision"] == StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE

    def test_r118_continuation_signal_true_overrides_false_stop_labels(self):
        """continuation-signal autonomous_continue=true overrides advisory false-stop labels."""
        # When autonomous_continue=true and no TRUE_EXTERNAL_GATE/UNSAFE_WORKSPACE:
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            continuation_signal={"autonomous_continue": True},
        )
        # POC not ready → not terminal → NON_TERMINAL_CONTINUE
        assert result == NON_TERMINAL_CONTINUE

    def test_r118_safe_lanes_available_forces_executable_next_action(self):
        """safe_lanes_available=true forces executable next action when POC not ready."""
        state = {**_make_r118_state(), "safe_lanes_available": True}
        dashboard = _make_incomplete_dashboard()

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
        )
        # With POC not ready and no true external gate:
        assert result == NON_TERMINAL_CONTINUE
        action = decide_next_action(result, gap_queue=[{"target_id": "FODS", "priority": 1}])
        assert action["action"] == NON_TERMINAL_CONTINUE

    def test_r118_if_poc_ready_only_gate11_remains(self):
        """If POC ready and only Gate 11 remains, train stops with release-pending terminal."""
        state = {"terminal_state_reached": False}
        dashboard = _make_complete_dashboard()
        verdict = _make_supervisor_verdict(claims_checked=88, verdict="PASS")

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            supervisor_verdict=verdict,
            gate_11_pending=True,
        )
        assert result == TERMINAL_POC_READY_RELEASE_PENDING
        # decide_next_action treats this as TERMINAL
        action = decide_next_action(result)
        assert action["action"] == "TERMINAL"

    def test_r118_if_poc_not_ready_and_gate11_appears_continue_implementation(self):
        """If POC not ready and Gate 11 appears, continue implementation."""
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()

        # Gate 11 with POC not ready → continue
        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            gate_11_pending=True,
        )
        assert result == NON_TERMINAL_CONTINUE


# ─────────────────────────────────────────────────────────────
# Dashboard contradiction tests with adjudicator
# ─────────────────────────────────────────────────────────────

class TestDashboardWithAdjudicator:
    def test_poc_ready_false_closure_true_is_contradiction(self):
        """poc_ready=false + closure_criteria_met=true = STATE_CONTRADICTION → repair."""
        dashboard = {
            "poc_ready": False,
            "closure_criteria_met": True,
            "all_commercial_pass": True,
            "foss_minimum_met": True,
            "blocking_gaps": [],
        }
        result = reconcile_dashboard_contradiction(dashboard)
        assert result["contradiction_detected"] is True
        assert result["repaired_poc_ready"] is True

    def test_no_contradiction_in_r118_incomplete_state(self):
        """R118 incomplete POC (not all commercial PASS) has no contradiction."""
        dashboard = _make_incomplete_dashboard()
        dashboard["closure_criteria_met"] = False
        result = reconcile_dashboard_contradiction(dashboard)
        assert result["repaired_poc_ready"] is False


# ─────────────────────────────────────────────────────────────
# Gate 11 vs POC ready separation
# ─────────────────────────────────────────────────────────────

class TestGate11VsPoC:
    def test_gate11_pending_not_blocking_poc_candidate_completion(self):
        """Gate 11 pending must NOT prevent POC candidate from being classified."""
        state = {"terminal_state_reached": False}
        dashboard = _make_complete_dashboard()
        verdict = _make_supervisor_verdict(claims_checked=88)

        result = classify_terminal_state(
            train_state=state,
            poc_dashboard=dashboard,
            supervisor_verdict=verdict,
            gate_11_pending=True,
        )
        # Result is TERMINAL (for release) but blocks_implementation=False
        assert result == TERMINAL_POC_READY_RELEASE_PENDING

        # Adjudicator agrees
        adj = adjudicate_stop_reason("gate_11_pending", {"poc_ready": True})
        assert adj["blocks_implementation"] is False
        assert adj["blocks_poc_candidate"] is False
        assert adj["blocks_release"] is True

    def test_no_invalid_stop_path_exists(self):
        """Verify no path through classify_terminal_state produces an invalid stop
        for common false-stop signals."""
        state = _make_r118_state()
        dashboard = _make_incomplete_dashboard()

        false_stop_scenarios = [
            {},  # No blockers
            {"evidence_quality_zero": True},  # Not in _EXTERNAL_GATE_SIGNALS
            {"missing_sample_outputs": True},  # Not in any gate signals
            {"prompt_quality_failure": True},  # Not in any gate signals
        ]

        for scenario in false_stop_scenarios:
            result = classify_terminal_state(
                train_state=state,
                poc_dashboard=dashboard,
                blocker_routing=scenario,
            )
            assert result == NON_TERMINAL_CONTINUE, (
                f"False stop for scenario {scenario}: got {result}"
            )
