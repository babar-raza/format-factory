"""
test_stop_reason_adjudicator.py — Tests for Stop Reason Adjudicator

All 18 rules must be covered. No false stops may pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

import pytest
from stop_reason_adjudicator import (
    StopDecision,
    SignalCategory,
    adjudicate_stop_reason,
    adjudicate_batch,
    reclassify_task_label,
    _normalize_signal,
)


# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────

def assert_not_terminal(result):
    assert result["terminal"] is False, (
        f"Expected non-terminal but got terminal=True for signal={result['input_signal']} "
        f"decision={result['decision']}"
    )
    assert result["blocks_implementation"] is False


def assert_terminal(result):
    assert result["terminal"] is True, (
        f"Expected terminal but got terminal=False for signal={result['input_signal']} "
        f"decision={result['decision']}"
    )


def assert_agent_can_handle(result):
    assert result["agent_can_handle"] is True, (
        f"Expected agent_can_handle=True for {result['input_signal']}"
    )


# ─────────────────────────────────────────────────────────────
# Rule 1: Supervisor ACCEPTED
# ─────────────────────────────────────────────────────────────

class TestRule1SupervisorAccepted:
    def test_accepted_alone_is_not_terminal(self):
        result = adjudicate_stop_reason("supervisor_accepted")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CONTINUE_NEXT_ITERATION

    def test_accepted_with_poc_ready_and_gate11_is_release_pending(self):
        result = adjudicate_stop_reason(
            "supervisor_accepted",
            {"poc_ready": True, "gate_11_pending": True}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER
        assert result["blocks_implementation"] is False
        assert result["blocks_poc_candidate"] is False
        assert result["blocks_release"] is True

    def test_accepted_with_poc_ready_no_gate11(self):
        result = adjudicate_stop_reason("supervisor_accepted", {"poc_ready": True})
        assert_terminal(result)
        assert result["decision"] == StopDecision.POC_READY_CANDIDATE

    def test_accepted_with_rework_is_not_terminal(self):
        result = adjudicate_stop_reason("accepted_with_rework", {"rework_is_repairable": True})
        assert_not_terminal(result)

    def test_accepted_with_limitations_is_not_terminal(self):
        result = adjudicate_stop_reason("accepted_with_limitations")
        assert_not_terminal(result)

    def test_sprint_accepted_is_not_terminal(self):
        result = adjudicate_stop_reason("sprint_accepted")
        assert_not_terminal(result)

    def test_overall_verdict_accepted_is_not_terminal(self):
        result = adjudicate_stop_reason("overall_verdict_accepted")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 3: Evidence package built
# ─────────────────────────────────────────────────────────────

class TestRule3EvidencePackageBuilt:
    def test_evidence_package_built_not_terminal(self):
        result = adjudicate_stop_reason("evidence_package_built")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CONTINUE_NEXT_ITERATION

    def test_review_package_created_not_terminal(self):
        result = adjudicate_stop_reason("review_package_created")
        assert_not_terminal(result)

    def test_review_package_built_not_terminal(self):
        result = adjudicate_stop_reason("review_package_built")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 4: Evidence quality zero
# ─────────────────────────────────────────────────────────────

class TestRule4EvidenceQualityZero:
    def test_quality_zero_repairable_is_local_repair(self):
        result = adjudicate_stop_reason("evidence_quality_zero", {"materialization_verified": True})
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.LOCAL_REPAIR_CONTINUE

    def test_quality_zero_default_is_local_repair(self):
        result = adjudicate_stop_reason("evidence_quality_zero")
        assert_not_terminal(result)
        assert result["decision"] in (
            StopDecision.LOCAL_REPAIR_CONTINUE,
            StopDecision.STATE_CONTRADICTION_REPAIR_REQUIRED,
        )

    def test_quality_zero_corrupted_is_unsafe(self):
        result = adjudicate_stop_reason(
            "evidence_quality_zero",
            {"evidence_system_corrupted": True}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.UNSAFE_WORKSPACE

    def test_missing_sample_outputs_not_terminal(self):
        result = adjudicate_stop_reason("missing_sample_outputs")
        assert_not_terminal(result)

    def test_missing_raw_logs_not_terminal(self):
        result = adjudicate_stop_reason("missing_raw_logs")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 5: Prompt quality failure
# ─────────────────────────────────────────────────────────────

class TestRule5PromptQuality:
    def test_prompt_quality_failure_not_terminal(self):
        result = adjudicate_stop_reason("prompt_quality_failure")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.LOCAL_REPAIR_CONTINUE

    def test_wrong_stream_not_terminal(self):
        result = adjudicate_stop_reason("wrong_stream_next_sprint")
        assert_not_terminal(result)

    def test_prompt_unsafe_edit_is_unsafe_workspace(self):
        result = adjudicate_stop_reason(
            "prompt_quality_failure",
            {"prompt_would_cause_unsafe_edit": True}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.UNSAFE_WORKSPACE

    def test_anti_skip_false_positive_not_terminal(self):
        result = adjudicate_stop_reason("anti_skip_false_positive")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 6: Max iterations
# ─────────────────────────────────────────────────────────────

class TestRule6MaxIterations:
    def test_max_iterations_is_checkpoint_rollover(self):
        result = adjudicate_stop_reason("max_iterations_reached")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CHECKPOINT_ROLLOVER_CONTINUE

    def test_max_iterations_variant(self):
        result = adjudicate_stop_reason("max_iterations")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CHECKPOINT_ROLLOVER_CONTINUE

    def test_iteration_limit_reached(self):
        result = adjudicate_stop_reason("iteration_limit_reached")
        assert_not_terminal(result)

    def test_agent_can_handle_max_iterations(self):
        result = adjudicate_stop_reason("max_iterations_reached")
        assert_agent_can_handle(result)
        assert result["human_required"] is False


# ─────────────────────────────────────────────────────────────
# Rule 7: MODE 5 / MCP
# ─────────────────────────────────────────────────────────────

class TestRule7ModeApproval:
    def test_mode5_pending_not_terminal(self):
        result = adjudicate_stop_reason("mode_5_approval_pending")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE

    def test_autonomous_sprint_loop_not_terminal(self):
        result = adjudicate_stop_reason("autonomous_sprint_loop_approval_required")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE

    def test_mcp_daemon_not_requiring_external_not_terminal(self):
        result = adjudicate_stop_reason("mcp_daemon_required", {"requires_external_daemon": False})
        assert_not_terminal(result)

    def test_mcp_requiring_external_daemon_is_external_gate(self):
        result = adjudicate_stop_reason(
            "mcp_daemon_required",
            {"requires_external_daemon": True}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE


# ─────────────────────────────────────────────────────────────
# Rule 8: Ruflo unavailable
# ─────────────────────────────────────────────────────────────

class TestRule8RufloUnavailable:
    def test_ruflo_unavailable_is_fallback(self):
        result = adjudicate_stop_reason("ruflo_unavailable")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE

    def test_claude_flow_unavailable_is_fallback(self):
        result = adjudicate_stop_reason("claude_flow_unavailable")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE

    def test_superpowers_unavailable_is_fallback(self):
        result = adjudicate_stop_reason("superpowers_unavailable")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 9: Gate 11 pending
# ─────────────────────────────────────────────────────────────

class TestRule9Gate11:
    def test_gate11_pending_poc_not_ready_continues(self):
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": False})
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CONTINUE_NEXT_ITERATION
        assert result["blocks_implementation"] is False

    def test_gate11_required_poc_not_ready_continues(self):
        result = adjudicate_stop_reason("gate_11_required")
        assert_not_terminal(result)

    def test_gate11_pending_poc_ready_is_release_pending(self):
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": True})
        assert_terminal(result)
        assert result["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER
        assert result["blocks_implementation"] is False
        assert result["blocks_poc_candidate"] is False
        assert result["blocks_release"] is True

    def test_gate11_agent_prepares_packet(self):
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": True})
        assert result["agent_can_handle"] is True
        assert "packet" in result["allowed_next_action"].lower() or "gate 11" in result["allowed_next_action"].lower()

    def test_gate11_approval_keyword_not_terminal_if_poc_not_ready(self):
        result = adjudicate_stop_reason("gate11_approval_required", {"poc_ready": False})
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 10: Gate 8
# ─────────────────────────────────────────────────────────────

class TestRule10Gate8:
    def test_gate8_pending_poc_not_ready_continues(self):
        result = adjudicate_stop_reason("gate_8_pending")
        assert_not_terminal(result)

    def test_gate8_required_poc_not_ready_continues(self):
        result = adjudicate_stop_reason("gate_8_required")
        assert_not_terminal(result)

    def test_gate8_pending_poc_ready_is_release_pending(self):
        result = adjudicate_stop_reason("gate_8_pending", {"poc_ready": True})
        assert_terminal(result)
        assert result["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER


# ─────────────────────────────────────────────────────────────
# Rule 11: Commit/push
# ─────────────────────────────────────────────────────────────

class TestRule11CommitPush:
    def test_git_push_required_is_external_gate(self):
        result = adjudicate_stop_reason("git_push_required")
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE
        assert result["human_required"] is True

    def test_git_commit_required_is_external_gate(self):
        result = adjudicate_stop_reason("git_commit_required")
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE

    def test_commit_required_is_external_gate(self):
        result = adjudicate_stop_reason("commit_required")
        assert_terminal(result)

    def test_push_required_is_external_gate(self):
        result = adjudicate_stop_reason("push_required")
        assert_terminal(result)

    def test_agent_can_prepare_commit_summary(self):
        result = adjudicate_stop_reason("git_push_required")
        # Agent prepares summary; human executes
        assert result["agent_can_handle"] is True
        assert "Agent" in result["allowed_next_action"] or "prepare" in result["allowed_next_action"].lower()


# ─────────────────────────────────────────────────────────────
# Rule 12: Publication
# ─────────────────────────────────────────────────────────────

class TestRule12Publication:
    def test_publication_required_is_external_gate(self):
        result = adjudicate_stop_reason("publication_required")
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE

    def test_nuget_publish_required_is_external_gate(self):
        result = adjudicate_stop_reason("nuget_publish_required")
        assert_terminal(result)

    def test_pypi_publish_required_is_external_gate(self):
        result = adjudicate_stop_reason("pypi_publish_required")
        assert_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 13: Credentials
# ─────────────────────────────────────────────────────────────

class TestRule13Credentials:
    def test_credentials_required_no_fallback_is_external_gate(self):
        result = adjudicate_stop_reason("credentials_required", {"safe_fallback_exists": False})
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE

    def test_credentials_with_safe_fallback_is_local_repair(self):
        result = adjudicate_stop_reason("credentials_required", {"safe_fallback_exists": True})
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.LOCAL_REPAIR_CONTINUE


# ─────────────────────────────────────────────────────────────
# Rule 14: Destructive cleanup
# ─────────────────────────────────────────────────────────────

class TestRule14Destructive:
    def test_destructive_no_alternative_is_external_gate(self):
        result = adjudicate_stop_reason(
            "destructive_cleanup_required",
            {"non_destructive_alternative_exists": False}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE

    def test_destructive_with_alternative_is_local_repair(self):
        result = adjudicate_stop_reason(
            "destructive_cleanup_required",
            {"non_destructive_alternative_exists": True}
        )
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.LOCAL_REPAIR_CONTINUE

    def test_git_reset_hard_no_alt_is_external_gate(self):
        result = adjudicate_stop_reason(
            "git_reset_hard_required",
            {"non_destructive_alternative_exists": False}
        )
        assert_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 15: Business decision
# ─────────────────────────────────────────────────────────────

class TestRule15BusinessDecision:
    def test_business_decision_policy_can_infer_is_agent_recommendation(self):
        result = adjudicate_stop_reason(
            "business_decision_required",
            {"policy_can_infer_safely": True}
        )
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.AGENT_OWNED_RECOMMENDATION_CONTINUE

    def test_business_decision_cannot_infer_is_external_gate(self):
        result = adjudicate_stop_reason(
            "business_decision_required",
            {"policy_can_infer_safely": False}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.TRUE_EXTERNAL_GATE


# ─────────────────────────────────────────────────────────────
# Rule 16: DIF/SYLK/ZST / poc-targets delta
# ─────────────────────────────────────────────────────────────

class TestRule16ProductGap:
    def test_dif_reconsideration_is_agent_recommendation(self):
        result = adjudicate_stop_reason("dif_reconsideration")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.AGENT_OWNED_RECOMMENDATION_CONTINUE

    def test_sylk_promotion_is_agent_recommendation(self):
        result = adjudicate_stop_reason("sylk_promotion")
        assert_not_terminal(result)

    def test_zst_promotion_is_agent_recommendation(self):
        result = adjudicate_stop_reason("zst_promotion")
        assert_not_terminal(result)

    def test_poc_targets_proposed_delta_is_agent_recommendation(self):
        result = adjudicate_stop_reason("poc_targets_proposed_delta")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.AGENT_OWNED_RECOMMENDATION_CONTINUE

    def test_dogfood_gap_pending_is_agent_recommendation(self):
        result = adjudicate_stop_reason("dogfood_gap_pending")
        assert_not_terminal(result)

    def test_target_writer_missing_is_agent_recommendation(self):
        result = adjudicate_stop_reason("target_writer_missing")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Rule 18: Dirty git state
# ─────────────────────────────────────────────────────────────

class TestRule18DirtyGit:
    def test_classified_dirty_state_not_terminal(self):
        result = adjudicate_stop_reason("unsafe_workspace", {"dirty_state_classified": True})
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CONTINUE_NEXT_ITERATION

    def test_source_corruption_is_unsafe_workspace(self):
        result = adjudicate_stop_reason("source_corruption")
        assert_terminal(result)
        assert result["decision"] == StopDecision.UNSAFE_WORKSPACE

    def test_repeated_foundational_failure_is_unsafe(self):
        result = adjudicate_stop_reason("repeated_foundational_failure_3x")
        assert_terminal(result)
        assert result["decision"] == StopDecision.UNSAFE_WORKSPACE

    def test_unclassified_dirty_state_is_local_repair(self):
        result = adjudicate_stop_reason("unsafe_workspace")
        assert_not_terminal(result)


# ─────────────────────────────────────────────────────────────
# Generic "approval-blocked"/"blocked" — never sufficient to stop
# ─────────────────────────────────────────────────────────────

class TestGenericApprovalBlocked:
    def test_approval_blocked_generic_is_agent_review(self):
        result = adjudicate_stop_reason("approval_blocked")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.AGENT_OWNED_REVIEW_CONTINUE

    def test_blocked_generic_is_agent_review(self):
        result = adjudicate_stop_reason("blocked")
        assert_not_terminal(result)

    def test_human_required_generic_is_agent_review(self):
        result = adjudicate_stop_reason("human_required")
        assert_not_terminal(result)

    def test_human_approval_required_generic_is_agent_review(self):
        result = adjudicate_stop_reason("human_approval_required")
        assert_not_terminal(result)

    def test_babar_approval_required_generic_with_poc_ready_is_release_pending(self):
        result = adjudicate_stop_reason("babar_approval_required", {"poc_ready": True})
        assert_terminal(result)
        assert result["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER


# ─────────────────────────────────────────────────────────────
# Batch adjudication
# ─────────────────────────────────────────────────────────────

class TestBatchAdjudication:
    def test_all_continuation_signals_not_terminal(self):
        result = adjudicate_batch([
            "supervisor_accepted",
            "evidence_package_built",
            "max_iterations_reached",
            "prompt_quality_failure",
        ])
        assert result["overall_terminal"] is False
        assert result["has_true_external_gate"] is False
        assert result["all_agent_owned"] is True

    def test_mixed_signals_reports_highest_severity(self):
        result = adjudicate_batch([
            "supervisor_accepted",
            "git_push_required",
            "max_iterations_reached",
        ])
        assert result["overall_terminal"] is True
        assert result["has_true_external_gate"] is True
        assert result["overall_decision"] == StopDecision.TRUE_EXTERNAL_GATE

    def test_unsafe_workspace_dominates(self):
        result = adjudicate_batch([
            "source_corruption",
            "supervisor_accepted",
        ])
        assert result["overall_terminal"] is True
        assert result["has_unsafe_workspace"] is True
        assert result["overall_decision"] == StopDecision.UNSAFE_WORKSPACE

    def test_gate11_poc_ready_in_batch(self):
        result = adjudicate_batch(
            ["gate_11_pending", "supervisor_accepted"],
            {"poc_ready": True}
        )
        assert result["overall_terminal"] is True
        assert result["has_release_pending"] is True
        assert result["overall_decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER


# ─────────────────────────────────────────────────────────────
# Task label reclassification
# ─────────────────────────────────────────────────────────────

class TestTaskLabelReclassification:
    def test_approval_blocked_gate11_is_reclassified_agent_owned(self):
        result = reclassify_task_label(
            "[approval-blocked]",
            "Advance FODS Gate 11 commercial readiness",
            {"poc_ready": False}
        )
        assert result["is_false_stop"] is True
        assert result["new_label"] in ("agent-owned", "release-approval-pending")

    def test_approval_blocked_commit_is_reclassified_external_gate(self):
        result = reclassify_task_label(
            "[approval-blocked]",
            "Commit uncommitted product code"
        )
        assert result["is_false_stop"] is True
        assert result["new_label"] == "external-gate"

    def test_blocked_zst_is_reclassified_agent_owned(self):
        result = reclassify_task_label("[blocked]", "Open ZST Gate 11 reconsideration")
        assert result["is_false_stop"] is True
        assert result["agent_can_execute"] is True

    def test_agent_owned_label_not_false_stop(self):
        result = reclassify_task_label("[agent-owned]", "Prepare FODS Gate 11 readiness packet")
        assert result["is_false_stop"] is False

    def test_dogfood_task_is_agent_owned(self):
        result = reclassify_task_label(
            "[approval-blocked]",
            "Implement dogfood CSV export target writer"
        )
        assert result["is_false_stop"] is True
        assert result["new_label"] == "agent-owned"
        assert result["agent_can_execute"] is True

    def test_mode5_task_is_ruflo_fallback(self):
        result = reclassify_task_label(
            "[approval-blocked]",
            "MODE 5 autonomous sprint loop"
        )
        assert result["is_false_stop"] is True
        assert result["agent_can_execute"] is True

    def test_publication_is_external_gate(self):
        result = reclassify_task_label(
            "[blocked]",
            "Publish NuGet package to external registry"
        )
        assert result["new_label"] == "external-gate"
        assert result["agent_can_execute"] is False


# ─────────────────────────────────────────────────────────────
# Signal normalization
# ─────────────────────────────────────────────────────────────

class TestSignalNormalization:
    def test_normalize_gate11_variants(self):
        assert _normalize_signal("gate_11_pending") == SignalCategory.GATE_11
        assert _normalize_signal("gate_11_required") == SignalCategory.GATE_11
        assert _normalize_signal("gate11_approval_required") == SignalCategory.GATE_11

    def test_normalize_evidence_variants(self):
        assert _normalize_signal("evidence_quality_zero") == SignalCategory.EVIDENCE_QUALITY
        assert _normalize_signal("evidence_quality_score_zero") == SignalCategory.EVIDENCE_QUALITY
        assert _normalize_signal("missing_sample_outputs") == SignalCategory.EVIDENCE_QUALITY

    def test_normalize_push_variants(self):
        assert _normalize_signal("git_push_required") == SignalCategory.PUSH_COMMIT
        assert _normalize_signal("git_commit_required") == SignalCategory.PUSH_COMMIT
        assert _normalize_signal("commit_required") == SignalCategory.PUSH_COMMIT

    def test_normalize_ruflo_variants(self):
        assert _normalize_signal("ruflo_unavailable") == SignalCategory.RUFLO_MODE
        assert _normalize_signal("claude_flow_unavailable") == SignalCategory.RUFLO_MODE
        assert _normalize_signal("superpowers_unavailable") == SignalCategory.RUFLO_MODE

    def test_normalize_unknown_falls_back(self):
        result = _normalize_signal("some_completely_unknown_signal_xyz")
        assert result == SignalCategory.UNKNOWN

    def test_normalize_empty_string(self):
        result = _normalize_signal("")
        assert result == SignalCategory.UNKNOWN


# ─────────────────────────────────────────────────────────────
# R118 fixture: latest state adjudication
# ─────────────────────────────────────────────────────────────

class TestR118StateAdjudication:
    """Verify that R118 state produces correct decisions."""

    def test_r118_supervisor_accepted_continues(self):
        """R118 state: autonomous_cycle exit 0 — should not stop."""
        result = adjudicate_stop_reason("supervisor_accepted", {"poc_ready": False})
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.CONTINUE_NEXT_ITERATION

    def test_r118_gate11_pending_not_blocking_implementation(self):
        """R118 Gate 11 is pending — must not block product implementation."""
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": False})
        assert_not_terminal(result)
        assert result["blocks_implementation"] is False

    def test_r118_mode5_falls_back_to_local(self):
        """R118 approval-gates has NEXT_HUMAN_GATE MODE 5 — must not stop local work."""
        result = adjudicate_stop_reason("mode_5_approval_pending")
        assert_not_terminal(result)
        assert result["decision"] == StopDecision.RUFLO_FALLBACK_LOCAL_CONTINUE

    def test_r118_approval_blocked_false_stops_reclassified(self):
        """R118 next-sprint has 'approval-blocked' tasks — must be reclassified."""
        for label in ["approval-blocked", "blocked", "human-required"]:
            result = reclassify_task_label(f"[{label}]", "Advance product deepening")
            assert result["is_false_stop"] is True, f"Expected false_stop for label={label}"

    def test_r118_dirty_state_classified_continues(self):
        """R118 has dirty git state classified as sprint work — must continue."""
        result = adjudicate_stop_reason(
            "unsafe_workspace",
            {"dirty_state_classified": True}
        )
        assert_not_terminal(result)

    def test_r118_poc_ready_gate11_is_release_pending_not_implementation_blocker(self):
        """R118 with POC-ready: Gate 11 = release-approval-pending, not blocked."""
        result = adjudicate_stop_reason(
            "gate_11_pending",
            {"poc_ready": True, "autonomous_continue": True}
        )
        assert_terminal(result)
        assert result["decision"] == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER
        assert result["blocks_implementation"] is False
        assert result["agent_can_handle"] is True
