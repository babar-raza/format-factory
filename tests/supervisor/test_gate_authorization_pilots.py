"""test_gate_authorization_pilots.py — Pilot tests A-E for gate authorization policy.

Verifies FORMAT_FACTORY_GATE_AUTHORIZATION_V1:
- Pilots A-E: core authorization scenarios (uncertainty, repair, options, Gate 11, parallel)
- TestNegativeControls: false blockers rejected, valid Gate 11 accepted

TC-AUTH-009 (playful-dazzling-elephant plan)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

from stop_reason_adjudicator import (
    StopDecision,
    adjudicate_stop_reason,
    reclassify_task_label,
)
from governance_validators_gate_auth import (
    validate_premature_human_authorization_request,
    validate_gate_transition_state_machine,
)


class TestPilotAUncertaintyBelowGate11:
    """Pilot A: Agent with incomplete context continues autonomously."""

    def test_incomplete_spec_context_continues(self):
        result = adjudicate_stop_reason("evidence_quality_zero")
        assert result["terminal"] is False
        assert result["blocks_implementation"] is False
        assert result["decision"] != StopDecision.TRUE_EXTERNAL_GATE

    def test_uncertain_gate_assignment_continues(self):
        result = adjudicate_stop_reason("unknown", {"poc_ready": False})
        assert result["terminal"] is False

    def test_missing_evidence_is_local_repair_not_stop(self):
        result = adjudicate_stop_reason("missing_sample_outputs")
        assert result["terminal"] is False
        assert result["agent_can_handle"] is True

    def test_uncertainty_never_produces_true_external_gate(self):
        for signal in ["missing_context", "unclear_spec", "uncertain_implementation"]:
            result = adjudicate_stop_reason(signal)
            assert result["decision"] != StopDecision.TRUE_EXTERNAL_GATE, \
                f"Uncertainty signal '{signal}' incorrectly classified as TRUE_EXTERNAL_GATE"


class TestPilotBRepairableFailure:
    """Pilot B: Repairable failure routes to repair, not human escalation."""

    def test_overclaimed_item_routes_to_local_repair(self):
        result = adjudicate_stop_reason("accepted_with_rework", {"rework_is_repairable": True})
        assert result["terminal"] is False
        assert result["agent_can_handle"] is True

    def test_failed_validation_does_not_produce_gate_11(self):
        result = adjudicate_stop_reason("accepted_with_rework")
        assert result["decision"] != StopDecision.WAITING_GATE_11_AUTHORIZATION
        assert result["decision"] != StopDecision.TRUE_EXTERNAL_GATE

    def test_v80_repairable_in_place(self):
        # A declaration with a false human blocker is flagged by V80
        # The agent repairs the item's notes field and reruns — no escalation
        declaration_bad = {
            "planned_work_items": [{
                "item_id": "ITEM-001",
                "title": "Implement FODS parser",
                "status": "blocked_external_gate",
                "item_type": "PRODUCT_SOURCE",
                "notes": "human authorization required before proceeding",
            }]
        }
        result_bad = validate_premature_human_authorization_request(declaration_bad)
        assert result_bad["result"] == "FAIL"
        assert result_bad["blocks_sprint"] is True

        # After repair: notes updated with legitimate reason
        declaration_fixed = {
            "planned_work_items": [{
                "item_id": "ITEM-001",
                "title": "Implement FODS parser",
                "status": "not_started",
                "item_type": "PRODUCT_SOURCE",
                "notes": "now ready to implement",
            }]
        }
        result_fixed = validate_premature_human_authorization_request(declaration_fixed)
        assert result_fixed["result"] == "PASS"


class TestPilotCMultipleOptions:
    """Pilot C: Multiple options trigger evidence-based selection, not escalation."""

    def test_product_gap_does_not_escalate(self):
        for signal in ["poc_targets_proposed_delta", "dif_reconsideration", "dogfood_gap_pending"]:
            result = adjudicate_stop_reason(signal)
            assert result["terminal"] is False
            assert result["human_required"] is False, \
                f"'{signal}' incorrectly set human_required=True"

    def test_implementation_gate_is_agent_handleable(self):
        result = adjudicate_stop_reason("blocked_local")
        assert result["terminal"] is False

    def test_multiple_options_reclassified_as_agent_owned(self):
        result = reclassify_task_label(
            "[approval-blocked]",
            "Choose between FODS writer implementation strategies"
        )
        assert result["is_false_stop"] is True
        assert result["agent_can_execute"] is True


class TestPilotDValidGate11Transition:
    """Pilot D: Correct Gate 11 request is accepted; premature ones are rejected."""

    def test_gate10_complete_and_poc_ready_produces_gate11_waiting(self):
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": True})
        assert result["decision"] == StopDecision.WAITING_GATE_11_AUTHORIZATION
        assert result["blocks_implementation"] is False
        assert result["blocks_release"] is True
        assert result["agent_can_handle"] is True

    def test_waiting_gate_11_is_alias_for_release_approval_pending(self):
        assert (
            StopDecision.WAITING_GATE_11_AUTHORIZATION
            == StopDecision.RELEASE_APPROVAL_PENDING_NOT_IMPLEMENTATION_BLOCKER
        )

    def test_v81_rejects_non_release_item_claiming_gate_11(self):
        declaration_bad = {
            "planned_work_items": [{
                "item_id": "ITEM-001",
                "title": "Implement FODS spec",
                "status": "blocked_external_gate",
                "item_type": "PRODUCT_SOURCE",
                "gate_ref": "11",
            }]
        }
        result = validate_gate_transition_state_machine(declaration_bad)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_v80_rejects_product_source_with_human_blocker(self):
        declaration = {
            "planned_work_items": [{
                "item_id": "ITEM-002",
                "title": "Implement FODT writer",
                "status": "blocked_external_gate",
                "item_type": "PRODUCT_SOURCE",
                "notes": "awaiting human approval to proceed",
            }]
        }
        result = validate_premature_human_authorization_request(declaration)
        assert result["result"] == "FAIL"

    def test_valid_gate11_release_item_passes_both_validators(self):
        declaration_good = {
            "planned_work_items": [{
                "item_id": "GATE11-FODS",
                "title": "FODS Gate 11 Commercial Release",
                "status": "blocked_external_gate",
                "item_type": "RELEASE_GATE",
                "gate_ref": "11",
                "notes": "Awaiting Babar Raza Gate 11 G11-G commercial release execution approval",
            }]
        }
        v80 = validate_premature_human_authorization_request(declaration_good)
        assert v80["result"] == "PASS", f"V80 false-positived on valid Gate 11 item: {v80}"
        v81 = validate_gate_transition_state_machine(declaration_good)
        assert v81["result"] == "PASS", f"V81 false-positived on valid Gate 11 item: {v81}"


class TestPilotEParallelLanes:
    """Pilot E: Gate 11 wait for one product does not block other products."""

    def test_gate11_does_not_block_implementation(self):
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": True})
        assert result["blocks_implementation"] is False

    def test_safe_lanes_available_signals_continue(self):
        result = adjudicate_stop_reason(
            "gate_11_pending",
            {"poc_ready": True, "safe_lanes_available": True}
        )
        assert result["blocks_implementation"] is False
        assert result["agent_can_handle"] is True

    def test_gate11_blocks_release_only(self):
        result = adjudicate_stop_reason("gate_11_pending", {"poc_ready": True})
        assert result["blocks_release"] is True
        assert result["blocks_poc_candidate"] is False

    def test_independent_product_continues_during_gate11_wait(self):
        # Simulate: FODS at Gate 11, FODT at Gate 7 (implementation)
        # FODT lane must continue — Gate 11 for FODS does not stop FODT work
        result_fodt = adjudicate_stop_reason("gate_11_pending", {"poc_ready": False})
        # poc_ready=False for FODT → CONTINUE_NEXT_ITERATION (not RELEASE_APPROVAL_PENDING)
        assert result_fodt["decision"] == StopDecision.CONTINUE_NEXT_ITERATION
        assert result_fodt["terminal"] is False


class TestNegativeControls:
    """Negative controls: false blockers are rejected, valid Gate 11 requests are accepted."""

    def test_generic_human_approval_is_not_terminal(self):
        result = adjudicate_stop_reason("human_approval_required")
        assert result["terminal"] is False

    def test_approval_blocked_label_is_false_stop(self):
        result = reclassify_task_label("[approval-blocked]", "Implement CSV parser")
        assert result["is_false_stop"] is True
        assert result["agent_can_execute"] is True

    def test_blocked_label_alone_is_false_stop(self):
        result = reclassify_task_label("[blocked]", "Repair test failures")
        assert result["is_false_stop"] is True

    def test_babar_required_without_poc_does_not_stop(self):
        result = adjudicate_stop_reason("babar_approval_required", {"poc_ready": False})
        assert result["terminal"] is False

    def test_v80_clean_declaration_passes(self):
        result = validate_premature_human_authorization_request({"planned_work_items": []})
        assert result["result"] == "PASS"

    def test_v81_clean_declaration_passes(self):
        result = validate_gate_transition_state_machine({"planned_work_items": []})
        assert result["result"] == "PASS"

    def test_v80_human_gate_item_type_fails(self):
        """V80 must detect human gate item_type even without phrase matching (RISK-04 coverage)."""
        declaration = {
            "planned_work_items": [{
                "item_id": "HGATE-001",
                "title": "Await product owner review",
                "status": "blocked_external_gate",
                "item_type": "HUMAN_GATE",
                "notes": "product owner must review before continuing",
            }]
        }
        result = validate_premature_human_authorization_request(declaration)
        assert result["result"] == "FAIL", \
            "V80 must detect HUMAN_GATE item_type as structural false human blocker"
        assert result["blocks_sprint"] is True

    def test_v80_manual_gate_item_type_fails(self):
        """V80 must detect MANUAL_GATE item_type (novel phrasing coverage)."""
        declaration = {
            "planned_work_items": [{
                "item_id": "MGATE-001",
                "title": "Manual sign-off checkpoint",
                "status": "not_started",
                "item_type": "MANUAL_GATE",
                "notes": "",
            }]
        }
        result = validate_premature_human_authorization_request(declaration)
        assert result["result"] == "FAIL"

    def test_v80_legitimate_credentials_blocker_passes(self):
        """V80 must NOT flag legitimate credential/push blockers."""
        declaration = {
            "planned_work_items": [{
                "item_id": "PUSH-001",
                "title": "Push changes to main",
                "status": "blocked_external_gate",
                "item_type": "GOVERNANCE_TASKCARD",
                "notes": "blocked: git push credentials unavailable",
            }]
        }
        result = validate_premature_human_authorization_request(declaration)
        assert result["result"] == "PASS", \
            f"V80 false-positived on legitimate credential blocker: {result}"

    def test_v80_legitimate_publication_blocker_passes(self):
        """V80 must NOT flag publication blockers."""
        declaration = {
            "planned_work_items": [{
                "item_id": "PUB-001",
                "title": "Publish to PyPI",
                "status": "blocked_external_gate",
                "item_type": "RELEASE_GATE",
                "notes": "blocked: publication credentials unavailable for pypi registry",
            }]
        }
        result = validate_premature_human_authorization_request(declaration)
        assert result["result"] == "PASS", \
            f"V80 false-positived on legitimate publication blocker: {result}"

    def test_v80_does_not_flag_release_gate_items(self):
        """V80 must not flag RELEASE_GATE items even with Babar Raza language."""
        declaration = {
            "planned_work_items": [{
                "item_id": "GATE11-001",
                "title": "Gate 11 Approval Request",
                "status": "blocked_external_gate",
                "item_type": "RELEASE_GATE",
                "gate_ref": "11",
                "notes": "human authorization required: Babar Raza must approve Gate 11",
            }]
        }
        result = validate_premature_human_authorization_request(declaration)
        assert result["result"] == "PASS", \
            f"V80 incorrectly flagged RELEASE_GATE item: {result}"
