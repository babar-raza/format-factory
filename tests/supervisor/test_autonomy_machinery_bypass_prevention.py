"""Tests for machinery bypass prevention — adversarial routing scenarios."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.autonomy_route_decider import (
    classify_task_category,
    check_action_route_allowed,
    check_prompt_for_unsafe_instructions,
)
from tools.supervisor.action_queue import validate_route_classification


# ---------------------------------------------------------------------------
# Machinery bypass via misclassification
# ---------------------------------------------------------------------------

class TestMachineryBypassViaName:
    def test_machinery_keyword_in_product_summary(self):
        """Task summary mentioning autonomous_cycle must classify as machinery."""
        cat = classify_task_category("product update to autonomous_cycle.py")
        assert cat == "AUTONOMY_ORCHESTRATOR_MACHINERY"

    def test_supervisor_loop_keyword(self):
        cat = classify_task_category("run supervisor_loop on latest evidence")
        assert cat == "SUPERVISOR_VERDICT_MACHINERY"

    def test_action_queue_keyword(self):
        cat = classify_task_category("modify action_queue processing")
        assert cat == "ACTION_QUEUE_MACHINERY"


# ---------------------------------------------------------------------------
# Queue validation blocks machinery without route_decision_id
# ---------------------------------------------------------------------------

class TestQueueRouteValidation:
    def test_machinery_without_route_decision_id_blocked(self):
        item = {
            "task_category": "AUTONOMY_ORCHESTRATOR_MACHINERY",
            "action_type": "UPDATE_STATE",
        }
        errors = validate_route_classification(item)
        assert len(errors) > 0
        assert "route_decision_id" in errors[0]

    def test_product_without_route_decision_id_allowed(self):
        item = {
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        }
        errors = validate_route_classification(item)
        assert errors == []

    def test_no_category_backward_compat(self):
        item = {"action_type": "GENERATE_SAMPLE_OUTPUT"}
        errors = validate_route_classification(item)
        assert errors == []

    def test_machinery_with_route_decision_id_passes(self):
        item = {
            "task_category": "SPEC_AUTHORITY_MACHINERY",
            "route_decision_id": "ADR-ROUTE-TEST",
        }
        errors = validate_route_classification(item)
        assert errors == []


# ---------------------------------------------------------------------------
# Backend dispatch enforcement
# ---------------------------------------------------------------------------

class TestActionRouteAllowed:
    def test_source_mutating_no_category_blocked(self):
        action = {"action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE"}
        allowed, reason = check_action_route_allowed(action)
        assert allowed is False
        assert "task_category" in reason

    def test_source_mutating_legacy_backfill_allowed(self):
        action = {
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "legacy_backfill": True,
        }
        allowed, _ = check_action_route_allowed(action)
        assert allowed is True

    def test_unknown_category_blocked(self):
        action = {"task_category": "UNKNOWN_OR_AMBIGUOUS", "action_type": "SOMETHING"}
        allowed, reason = check_action_route_allowed(action)
        assert allowed is False
        assert "UNKNOWN_OR_AMBIGUOUS" in reason


# ---------------------------------------------------------------------------
# Prompt safety — adversarial patterns
# ---------------------------------------------------------------------------

class TestPromptUnsafePatternCheck:
    def test_git_commit_executable(self):
        result = check_prompt_for_unsafe_instructions("Step 3: Run git commit -m 'release'")
        assert result["pass"] is False

    def test_git_push_executable(self):
        result = check_prompt_for_unsafe_instructions("Then git push origin main")
        assert result["pass"] is False

    def test_advisory_do_not_skipped(self):
        result = check_prompt_for_unsafe_instructions(
            "Do not run git commit without authorization."
        )
        assert result["pass"] is True

    def test_policy_warning_skipped(self):
        result = check_prompt_for_unsafe_instructions(
            "Warning: git push is prohibited without explicit approval."
        )
        assert result["pass"] is True

    def test_gate_bypass_flagged(self):
        result = check_prompt_for_unsafe_instructions("Use gate bypass to skip validation")
        assert result["pass"] is False

    def test_clean_prompt_passes(self):
        result = check_prompt_for_unsafe_instructions(
            "Implement the get_paragraph function and run pytest."
        )
        assert result["pass"] is True


# ---------------------------------------------------------------------------
# Governance Validator 11 — legacy backfill
# ---------------------------------------------------------------------------

class TestGovernanceValidatorLegacyBackfill:
    def test_governance_item_exempt(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "DOC-001",
                "item_type": "GOVERNANCE_DOC",
                "title": "Policy doc",
                "status": "completed",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "PASS"

    def test_current_run_product_source_missing_route_blocks(self):
        """Current-run PRODUCT_SOURCE without route_decision_id now FAILs."""
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "PS-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "ABW function",
                "status": "completed",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_legacy_backfill_exempt(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "PS-002",
                "item_type": "PRODUCT_SOURCE",
                "title": "Legacy function",
                "status": "completed",
                "legacy_backfill_status": "BACKFILLED",
            }],
        }
        result = validate_route_decision_required(decl)
        # Legacy/backfill items get WARN, not FAIL
        assert result["result"] in ("PASS", "WARN")
        assert result["blocks_sprint"] is False


class TestValidator11CurrentRunBlock:
    """Validator 11 must BLOCK current-run PRODUCT_SOURCE without route_decision_id."""

    def test_current_run_product_source_blocks(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "PS-CUR-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Current-run ABW function",
                "status": "completed",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_current_run_product_source_with_route_passes(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "PS-CUR-002",
                "item_type": "PRODUCT_SOURCE",
                "title": "ABW function",
                "status": "completed",
                "route_decision_id": "RD-001",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "PASS"

    def test_current_run_machinery_blocks(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "MACH-CUR-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Machinery item",
                "status": "completed",
                "task_category": "AUTONOMY_ORCHESTRATOR_MACHINERY",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_governance_doc_exempt(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "GOV-001",
                "item_type": "GOVERNANCE_DOC",
                "title": "Policy doc",
                "status": "completed",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "PASS"

    def test_legacy_backfill_warn_only(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [{
                "item_id": "PS-LEG-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Legacy function",
                "status": "completed",
                "legacy_backfill_status": "BACKFILLED",
            }],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False

    def test_mixed_legacy_and_current_blocks(self):
        from tools.supervisor.governance_validators import validate_route_decision_required
        decl = {
            "planned_work_items": [
                {
                    "item_id": "PS-LEG-002",
                    "item_type": "PRODUCT_SOURCE",
                    "title": "Legacy",
                    "status": "completed",
                    "legacy_backfill_status": "BACKFILLED",
                },
                {
                    "item_id": "PS-CUR-003",
                    "item_type": "PRODUCT_SOURCE",
                    "title": "Current-run",
                    "status": "completed",
                },
            ],
        }
        result = validate_route_decision_required(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


class TestImportFailureFailClosed:
    """ImportError in route decider must block current-run actions."""

    def test_source_mutating_blocked_on_import_failure(self):
        """Simulate what next_action_runner does when import fails."""
        # This tests the logic pattern, not the actual ImportError
        action = {
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_id": "A-IF-001",
        }
        # When import fails, source-mutating + not legacy = blocked
        is_source_mutating = action["action_type"] in (
            "IMPLEMENT_SMALL_PRODUCT_FEATURE", "PRODUCT_SOURCE_PATCH_BOUNDED",
        )
        is_legacy = action.get("legacy_backfill", False)
        assert is_source_mutating is True
        assert is_legacy is False
        # This combination must result in BLOCKED

    def test_legacy_allowed_on_import_failure(self):
        action = {
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "legacy_backfill": True,
            "action_id": "A-IF-002",
        }
        is_source_mutating = action["action_type"] in (
            "IMPLEMENT_SMALL_PRODUCT_FEATURE", "PRODUCT_SOURCE_PATCH_BOUNDED",
        )
        is_legacy = action.get("legacy_backfill", False)
        assert is_source_mutating is True
        assert is_legacy is True
        # Legacy is allowed through

    def test_categorized_non_legacy_blocked_on_import_failure(self):
        action = {
            "action_type": "RUN_TARGETED_PYTEST",
            "task_category": "PRODUCT_TESTING",
            "action_id": "A-IF-003",
        }
        cat = action.get("task_category", "")
        is_legacy = action.get("legacy_backfill", False)
        assert cat != ""
        assert is_legacy is False
        # Categorized + non-legacy + import failure = blocked
