"""
test_next_sprint_false_stop_regression.py — Regression Tests for Next-Sprint Generator

Verifies that generate_next_worker_prompt.py no longer emits false-stop labels
for agent-owned work, and that the Stop Reason Advisory is always present.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

from generate_next_worker_prompt import (
    generate_prompt,
    generate_next_work_items,
    STOP_REASON_ADVISORY,
    _make_task_adjudication_fields,
)

# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

def _r118_review() -> dict:
    """Minimal R118-like review fixture."""
    return {
        "sprint_id": "FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001",
        "run_id": "unified-poc-authority-reconciliation-r118",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "evidence_quality_score": 0.83,
        "item_grades": [],
        "test_results": {"passed": 0, "failed": 0, "skipped": 0},
    }


def _accepted_review_with_rework() -> dict:
    return {
        "sprint_id": "FORMAT-FACTORY-R119-MEGA-TRAIN-001",
        "run_id": "r119-test",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "item_grades": [
            {
                "item_id": "WI-001",
                "item_title": "Fix grading machinery",
                "supervisor_grade": "REWORK_REQUIRED",
                "required_rework": "Add tests_supporting field",
                "evidence_paths": [],
            }
        ],
        "test_results": {"passed": 100, "failed": 0, "skipped": 2},
    }


# ─────────────────────────────────────────────────────────────
# Advisory injection tests
# ─────────────────────────────────────────────────────────────

class TestAdvisoryInjection:
    def test_stop_reason_advisory_constant_contains_required_text(self):
        assert "ADVISORY ONLY" in STOP_REASON_ADVISORY
        assert "Stop Reason Adjudicator" in STOP_REASON_ADVISORY or "stop_reason_adjudicator" in STOP_REASON_ADVISORY
        assert "TRUE_EXTERNAL_GATE" in STOP_REASON_ADVISORY
        assert "UNSAFE_WORKSPACE" in STOP_REASON_ADVISORY

    def test_advisory_contains_false_stop_examples(self):
        assert "Supervisor ACCEPTED" in STOP_REASON_ADVISORY
        assert "max_iterations" in STOP_REASON_ADVISORY or "max iterations" in STOP_REASON_ADVISORY.lower()
        assert "Gate 11" in STOP_REASON_ADVISORY

    def test_advisory_contains_local_coordinator_fallback(self):
        assert "local coordinator" in STOP_REASON_ADVISORY.lower() or "RUFLO_FALLBACK" in STOP_REASON_ADVISORY

    def test_fallback_prompt_contains_advisory(self):
        """Generated fallback prompt must contain the advisory."""
        review = _r118_review()
        prompt = generate_prompt(review, repo_root=Path("."))
        # Advisory is embedded in fallback prompt
        assert "ADVISORY" in prompt or "Stop Reason" in prompt or "stop_reason" in prompt


# ─────────────────────────────────────────────────────────────
# False stop label tests
# ─────────────────────────────────────────────────────────────

class TestFalseStopLabels:
    def test_generated_items_have_no_approval_blocked_label(self):
        """No generated work item should have owner_classification='approval-blocked'."""
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        for item in result["items"]:
            label = item.get("owner_classification", "agent-owned")
            assert label != "approval-blocked", (
                f"Item {item['item_id']} has forbidden label 'approval-blocked'"
            )

    def test_generated_items_have_no_blocked_label(self):
        """No generated work item should have owner_classification='blocked'."""
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        for item in result["items"]:
            label = item.get("owner_classification", "agent-owned")
            assert label not in ("blocked", "human-required", "stop"), (
                f"Item {item['item_id']} has forbidden label '{label}'"
            )

    def test_rework_items_have_no_false_stop_label(self):
        review = _accepted_review_with_rework()
        result = generate_next_work_items(review, stream="mainstream")
        rework = [i for i in result["items"] if i["lane"] == "rework"]
        assert len(rework) == 1
        label = rework[0].get("owner_classification", "agent-owned")
        assert label not in ("approval-blocked", "blocked", "human-required", "stop")

    def test_product_items_have_agent_owned_label(self):
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        product_items = [i for i in result["items"] if i["lane"] == "product-advancement"]
        for item in product_items:
            label = item.get("owner_classification", "agent-owned")
            assert label in ("agent-owned", "release-approval-pending"), (
                f"Product item {item['item_id']} has unexpected label '{label}'"
            )

    def test_all_items_have_agent_can_execute_field(self):
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        for item in result["items"]:
            assert "agent_can_execute" in item, (
                f"Item {item['item_id']} missing agent_can_execute field"
            )
            assert "human_required" in item, (
                f"Item {item['item_id']} missing human_required field"
            )
            assert "execution_status" in item, (
                f"Item {item['item_id']} missing execution_status field"
            )
            assert "allowed_next_action" in item, (
                f"Item {item['item_id']} missing allowed_next_action field"
            )


# ─────────────────────────────────────────────────────────────
# Task adjudication field helper tests
# ─────────────────────────────────────────────────────────────

class TestTaskAdjudicationFields:
    def test_agent_owned_task_has_correct_fields(self):
        fields = _make_task_adjudication_fields("[agent-owned]", "Implement FODS feature")
        assert fields["agent_can_execute"] is True
        assert fields["human_required"] is False
        assert fields["execution_status"] == "executable"
        assert fields["owner_classification"] == "agent-owned"

    def test_approval_blocked_label_is_reclassified(self):
        fields = _make_task_adjudication_fields(
            "[approval-blocked]",
            "Advance FODS product deepening"
        )
        # Must not remain as 'approval-blocked'
        assert fields["owner_classification"] != "approval-blocked"

    def test_git_push_task_is_external_gate(self):
        fields = _make_task_adjudication_fields("[blocked]", "Execute git push to remote")
        assert fields["owner_classification"] == "external-gate"
        assert fields["agent_can_execute"] is False
        assert fields["human_required"] is True
        assert fields["execution_status"] == "external-gate-pending"

    def test_gate11_with_poc_ready_is_release_pending(self):
        fields = _make_task_adjudication_fields(
            "[approval-blocked]",
            "Advance FODS Gate 11 commercial readiness",
            {"poc_ready": True}
        )
        assert fields["owner_classification"] in ("agent-owned", "release-approval-pending")

    def test_mode5_task_is_agent_executable(self):
        fields = _make_task_adjudication_fields(
            "[approval-blocked]",
            "MODE 5 autonomous sprint loop approval"
        )
        assert fields["agent_can_execute"] is True
        assert fields["owner_classification"] in ("agent-owned", "release-approval-pending")


# ─────────────────────────────────────────────────────────────
# Work items metadata tests
# ─────────────────────────────────────────────────────────────

class TestWorkItemsMetadata:
    def test_result_contains_advisory_field(self):
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        assert "stop_reason_adjudicator_advisory" in result
        assert "ADVISORY ONLY" in result["stop_reason_adjudicator_advisory"]

    def test_result_contains_forbidden_labels_field(self):
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        assert "false_stop_labels_forbidden" in result
        assert "approval-blocked" in result["false_stop_labels_forbidden"]
        assert "blocked" in result["false_stop_labels_forbidden"]

    def test_gate11_pending_does_not_emit_blocked_label(self):
        """Given Gate 11 pending and POC ready, generator emits release-pending, not blocked."""
        review = _r118_review()
        result = generate_next_work_items(review, stream="mainstream")
        for item in result["items"]:
            assert item.get("owner_classification") != "blocked"

    def test_autonomous_continue_true_produces_executable_items(self):
        """Given autonomous_continue=true, generator produces items with agent_can_execute."""
        review = _r118_review()
        assert review["autonomous_continue"] is True
        result = generate_next_work_items(review, stream="mainstream")
        executable = [i for i in result["items"] if i.get("agent_can_execute") is True]
        assert len(executable) > 0, "No executable items generated despite autonomous_continue=true"

    def test_non_mainstream_stream_has_no_false_stop_labels(self):
        review = _r118_review()
        for stream in ("supervisor", "acceleration", "skills"):
            result = generate_next_work_items(review, stream=stream)
            for item in result["items"]:
                label = item.get("owner_classification", "agent-owned")
                assert label not in ("approval-blocked", "blocked", "human-required", "stop"), (
                    f"Stream={stream} item {item['item_id']} has forbidden label '{label}'"
                )

    def test_commit_task_would_be_external_gate(self):
        """A task about executing commit/push is correctly identified as external-gate."""
        fields = _make_task_adjudication_fields("[blocked]", "Execute git commit and push to main")
        assert fields["owner_classification"] == "external-gate"
        assert fields["execution_status"] == "external-gate-pending"

    def test_dogfood_writer_task_is_agent_owned(self):
        """Dogfood target writer implementation is agent-owned."""
        fields = _make_task_adjudication_fields(
            "[approval-blocked]",
            "Implement dogfood CSV target writer"
        )
        assert fields["agent_can_execute"] is True

    def test_zst_gate11_reconsideration_is_agent_owned(self):
        fields = _make_task_adjudication_fields("[blocked]", "Open ZST Gate 11 reconsideration")
        assert fields["agent_can_execute"] is True
        assert fields["owner_classification"] in ("agent-owned", "release-approval-pending")
