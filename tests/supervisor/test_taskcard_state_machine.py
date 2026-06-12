"""Tests for taskcard state machine enforcement (Lane F).

GRH-TC-006: Validate 15-state machine constants and enforcement rules.
Tests state transition validation, close-eligible states, and forbidden jump detection.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestStateConstants:
    def test_all_15_states_defined(self):
        from governance_validators import ALLOWED_TRANSITIONS
        expected = {
            "DISCOVERED", "EVIDENCE_LOCATED", "EXECUTION_CLASSIFIED",
            "CONTRACT_REQUIRED", "CONTRACTED", "IDEMPOTENCY_KEY_ASSIGNED",
            "MUTATION_BOUNDED", "MUTATION_EXECUTED", "DIFF_CAPTURED",
            "VALIDATED", "REPLAY_RECIPE_RECORDED", "REPLAY_TESTED",
            "GOVERNANCE_ACCEPTED", "BACKFILLED_LEGACY_ACCEPTED",
            "REJECTED_UNGOVERNED", "BLOCKED_INSUFFICIENT_EVIDENCE",
        }
        defined = set(ALLOWED_TRANSITIONS.keys())
        assert defined == expected, f"Missing states: {expected - defined}"

    def test_close_eligible_states_are_subset_of_all_states(self):
        from governance_validators import ALLOWED_TRANSITIONS, CLOSE_ELIGIBLE_STATES
        all_states = set(ALLOWED_TRANSITIONS.keys())
        assert CLOSE_ELIGIBLE_STATES.issubset(all_states)

    def test_governance_accepted_is_close_eligible(self):
        from governance_validators import CLOSE_ELIGIBLE_STATES
        assert "GOVERNANCE_ACCEPTED" in CLOSE_ELIGIBLE_STATES

    def test_backfilled_is_close_eligible(self):
        from governance_validators import CLOSE_ELIGIBLE_STATES
        assert "BACKFILLED_LEGACY_ACCEPTED" in CLOSE_ELIGIBLE_STATES

    def test_discovered_is_not_close_eligible(self):
        from governance_validators import CLOSE_ELIGIBLE_STATES
        assert "DISCOVERED" not in CLOSE_ELIGIBLE_STATES

    def test_terminal_states_have_no_outgoing(self):
        from governance_validators import ALLOWED_TRANSITIONS
        # Terminal states should have empty allowed_next
        for state in ("GOVERNANCE_ACCEPTED", "BACKFILLED_LEGACY_ACCEPTED"):
            assert len(ALLOWED_TRANSITIONS[state]) == 0, (
                f"{state} should be terminal but has outgoing: {ALLOWED_TRANSITIONS[state]}"
            )


class TestForbiddenJumps:
    def test_discovered_to_governance_accepted_forbidden_for_product(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {
            "planned_work_items": [{
                "item_id": "TC-001",
                "item_type": "PRODUCT_SOURCE",
                "product_track": "foss_python",
                "state_machine_start": "DISCOVERED",
                "state_machine_target": "GOVERNANCE_ACCEPTED",
                "status": "completed",
            }]
        }
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"
        assert "FORBIDDEN" in result["items"][0]["issue"]

    def test_discovered_to_governance_accepted_allowed_for_governance_doc(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {
            "planned_work_items": [{
                "item_id": "GR-TC-001",
                "item_type": "GOVERNANCE_DOC",
                "exception_classification": "investigation_only",
                "state_machine_start": "DISCOVERED",
                "state_machine_target": "GOVERNANCE_ACCEPTED",
                "status": "completed",
            }]
        }
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] in ("PASS", "WARN"), (
            f"Governance doc DISCOVERED→GOVERNANCE_ACCEPTED should not FAIL, got {result['result']}"
        )

    def test_execution_classified_to_governance_accepted_forbidden_for_product(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {
            "planned_work_items": [{
                "item_id": "TC-001",
                "item_type": "PRODUCT_SOURCE",
                "product_track": "foss_python",
                "state_machine_start": "EXECUTION_CLASSIFIED",
                "state_machine_target": "GOVERNANCE_ACCEPTED",
                "status": "completed",
            }]
        }
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"


class TestCloseEligibility:
    def test_completed_in_validated_state_passes(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {
            "planned_work_items": [{
                "item_id": "TC-001",
                "item_type": "PRODUCT_SOURCE",
                "state_machine_start": "DIFF_CAPTURED",
                "state_machine_target": "VALIDATED",
                "status": "completed",
                "execution_method": "MANUAL_GOVERNED_BY_SKILL",
            }]
        }
        result = validate_taskcard_state_transitions(decl)
        # VALIDATED is close-eligible → should not fail on close-eligibility
        # (it may fail on other checks but not CLOSE_ELIGIBLE)
        close_fail = any(
            "not close-eligible" in item.get("issue", "")
            for item in result.get("items", [])
        )
        assert not close_fail

    def test_completed_in_mutation_executed_not_close_eligible(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {
            "planned_work_items": [{
                "item_id": "TC-001",
                "item_type": "PRODUCT_SOURCE",
                "state_machine_start": "MUTATION_BOUNDED",
                "state_machine_target": "MUTATION_EXECUTED",
                "status": "completed",
                "execution_method": "MANUAL_GOVERNED_BY_SKILL",
            }]
        }
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] == "FAIL"
        assert any("not close-eligible" in item.get("issue", "") for item in result["items"])


class TestStateTransitionValidator:
    def test_backfilled_to_backfilled_accepted_passes(self):
        from governance_validators import validate_taskcard_state_transitions
        decl = {
            "planned_work_items": [{
                "item_id": "TC-006",
                "item_type": "LEGACY_BACKFILL_METADATA",
                "state_machine_start": "EVIDENCE_LOCATED",
                "state_machine_target": "BACKFILLED_LEGACY_ACCEPTED",
                "status": "completed",
                "execution_method": "BACKFILLED_LEGACY_EXECUTION",
                "claim_classification": "LEGACY_BACKFILLED",
            }]
        }
        result = validate_taskcard_state_transitions(decl)
        assert result["result"] in ("PASS", "WARN"), (
            f"BACKFILLED should not FAIL, got {result['result']}: {result.get('items')}"
        )

    def test_empty_declaration_passes(self):
        from governance_validators import validate_taskcard_state_transitions
        result = validate_taskcard_state_transitions({"planned_work_items": []})
        assert result["result"] == "PASS"
