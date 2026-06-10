"""Tests for autonomy_route_decider — core routing logic."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.autonomy_route_models import (
    ALL_ROUTES,
    ALL_TASK_CATEGORIES,
    REQUIRED_DECISION_FIELDS,
    ROUTE_AGENT_GOVERNED_DECISION_REQUIRED,
    ROUTE_AUTONOMOUS_ACCELERATED_DEFAULT,
    ROUTE_BLOCKED,
    ROUTE_GOVERNED_DIRECT_EXECUTION,
    ROUTE_HUMAN_APPROVAL_REQUIRED,
    SCHEMA_VERSION,
    TASK_CATEGORIES_MACHINERY,
    TASK_CATEGORIES_PRODUCT,
)
from tools.supervisor.autonomy_route_decider import (
    RouteDecision,
    classify_task_category,
    decide_route,
    validate_route_decision,
    check_machinery_mutation_allowed,
    check_action_route_allowed,
    check_prompt_for_unsafe_instructions,
    quarantine_unsafe_prompt,
)


# ---------------------------------------------------------------------------
# classify_task_category
# ---------------------------------------------------------------------------

class TestClassifyTaskCategory:
    def test_product_keyword_returns_product_implementation(self):
        cat = classify_task_category("Implement new ABW codec function")
        assert cat == "PRODUCT_IMPLEMENTATION"

    def test_machinery_keyword_returns_machinery_category(self):
        cat = classify_task_category("Update autonomous_cycle orchestrator")
        assert cat == "AUTONOMY_ORCHESTRATOR_MACHINERY"

    def test_action_type_mapping(self):
        cat = classify_task_category("do something", action_type="IMPLEMENT_SMALL_PRODUCT_FEATURE")
        assert cat == "PRODUCT_IMPLEMENTATION"

    def test_explicit_hint_overrides_all(self):
        cat = classify_task_category(
            "implement gnumeric function",
            action_type="UPDATE_STATE",
            hints={"task_category": "SPEC_AUTHORITY_MACHINERY"},
        )
        assert cat == "SPEC_AUTHORITY_MACHINERY"

    def test_unknown_for_no_match(self):
        cat = classify_task_category("do something completely unrelated xyz")
        assert cat == "UNKNOWN_OR_AMBIGUOUS"

    def test_machinery_keyword_map_governance_validator(self):
        cat = classify_task_category("Run governance_validator checks")
        assert cat == "VALIDATOR_OR_EVIDENCE_MACHINERY"

    def test_machinery_keyword_map_prompt_quality(self):
        cat = classify_task_category("Generate next prompt_quality report")
        assert cat == "PROMPT_GENERATION_MACHINERY"


# ---------------------------------------------------------------------------
# decide_route
# ---------------------------------------------------------------------------

class TestDecideRoute:
    def test_product_implementation_autonomous(self):
        d = decide_route(
            "T-001", "PRODUCT_IMPLEMENTATION", "Implement ABW function",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        assert d.final_route == ROUTE_AUTONOMOUS_ACCELERATED_DEFAULT
        assert d.autonomous_allowed is True
        assert d.blocked is False

    def test_product_missing_tests_not_autonomous(self):
        d = decide_route(
            "T-002", "PRODUCT_IMPLEMENTATION", "Implement ABW function",
            hints={"required_tests": [], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        assert d.final_route == ROUTE_AGENT_GOVERNED_DECISION_REQUIRED
        assert d.autonomous_allowed is False

    def test_unknown_category_blocked(self):
        d = decide_route("T-003", "UNKNOWN_OR_AMBIGUOUS", "Some vague task")
        assert d.final_route == ROUTE_BLOCKED
        assert d.blocked is True
        assert d.autonomous_allowed is False

    def test_invalid_category_blocked(self):
        d = decide_route("T-004", "NONEXISTENT_CATEGORY", "Bad task")
        assert d.final_route == ROUTE_BLOCKED
        assert d.blocked is True

    def test_machinery_no_decision_requires_governed(self):
        d = decide_route("T-005", "SPEC_AUTHORITY_MACHINERY", "Update spec authority")
        assert d.final_route == ROUTE_AGENT_GOVERNED_DECISION_REQUIRED
        assert d.autonomous_allowed is False

    def test_machinery_with_governed_decision(self):
        d = decide_route(
            "T-006", "SPEC_AUTHORITY_MACHINERY", "Update spec authority",
            hints={"governed_decision_present": True},
        )
        assert d.final_route == ROUTE_GOVERNED_DIRECT_EXECUTION
        assert d.machinery_mutation_allowed is True

    def test_high_risk_requires_human(self):
        d = decide_route(
            "T-007", "PRODUCT_IMPLEMENTATION", "Implement feature",
            risk_level="HIGH",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        assert d.final_route == ROUTE_HUMAN_APPROVAL_REQUIRED
        assert d.human_approval_required is True

    def test_explicit_human_approval_hint(self):
        d = decide_route(
            "T-008", "PRODUCT_TESTING", "Run tests",
            hints={"human_approval_required": True},
        )
        assert d.final_route == ROUTE_HUMAN_APPROVAL_REQUIRED

    def test_product_testing_autonomous(self):
        d = decide_route(
            "T-009", "PRODUCT_TESTING", "Run pytest",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["tests/"]},
        )
        assert d.final_route == ROUTE_AUTONOMOUS_ACCELERATED_DEFAULT

    def test_product_empty_required_tests_defeats_autonomy(self):
        """Verify that empty required_tests falls to AGENT_GOVERNED, not AUTONOMOUS."""
        d = decide_route(
            "T-010", "PRODUCT_IMPLEMENTATION", "Implement function",
            hints={"required_tests": [], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        assert d.final_route == ROUTE_AGENT_GOVERNED_DECISION_REQUIRED


# ---------------------------------------------------------------------------
# RouteDecision
# ---------------------------------------------------------------------------

class TestRouteDecision:
    def test_to_dict_has_all_required_fields(self):
        d = decide_route(
            "T-100", "PRODUCT_IMPLEMENTATION", "Test task",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        dd = d.to_dict()
        missing = REQUIRED_DECISION_FIELDS - set(dd.keys())
        assert missing == set(), f"Missing fields: {missing}"

    def test_write_and_load(self, tmp_path):
        d = decide_route(
            "T-101", "PRODUCT_IMPLEMENTATION", "Test task",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        path = d.write(output_dir=tmp_path)
        assert path.exists()
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["task_id"] == "T-101"
        assert loaded["schema_version"] == SCHEMA_VERSION


# ---------------------------------------------------------------------------
# validate_route_decision
# ---------------------------------------------------------------------------

class TestRouteDecisionValidation:
    def test_valid_decision_no_errors(self):
        d = decide_route(
            "T-200", "PRODUCT_IMPLEMENTATION", "Test",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        errors = validate_route_decision(d.to_dict())
        assert errors == []

    def test_missing_fields_detected(self):
        errors = validate_route_decision({"task_id": "X"})
        assert any("Missing required fields" in e for e in errors)

    def test_invalid_route_detected(self):
        d = decide_route(
            "T-201", "PRODUCT_IMPLEMENTATION", "Test",
            hints={"required_tests": ["t.py"], "required_evidence": ["e.json"], "allowed_paths": ["src/"]},
        )
        dd = d.to_dict()
        dd["final_route"] = "INVALID_ROUTE"
        errors = validate_route_decision(dd)
        assert any("Invalid final_route" in e for e in errors)

    def test_blocked_consistency(self):
        d = decide_route("T-202", "UNKNOWN_OR_AMBIGUOUS", "Vague")
        dd = d.to_dict()
        dd["blocked"] = False  # inconsistent with BLOCKED route
        errors = validate_route_decision(dd)
        assert any("BLOCKED route must have blocked=True" in e for e in errors)

    def test_blocked_no_machinery_mutation(self):
        d = decide_route("T-203", "UNKNOWN_OR_AMBIGUOUS", "Vague")
        dd = d.to_dict()
        dd["machinery_mutation_allowed"] = True
        errors = validate_route_decision(dd)
        assert any("blocked items must not have machinery_mutation_allowed" in e for e in errors)


# ---------------------------------------------------------------------------
# check_prompt_for_unsafe_instructions
# ---------------------------------------------------------------------------

class TestPromptUnsafeInstructions:
    def test_clean_prompt_passes(self):
        result = check_prompt_for_unsafe_instructions("Implement the function and run tests.")
        assert result["pass"] is True
        assert result["quarantine_needed"] is False

    def test_git_commit_outside_advisory_fails(self):
        result = check_prompt_for_unsafe_instructions("Now run git commit -m 'fix'")
        assert result["pass"] is False
        assert result["quarantine_needed"] is True

    def test_advisory_section_not_flagged(self):
        result = check_prompt_for_unsafe_instructions(
            "advisory: Do not run git commit or git push."
        )
        assert result["pass"] is True

    def test_policy_description_not_flagged(self):
        result = check_prompt_for_unsafe_instructions(
            "You must not use git push without authorization."
        )
        assert result["pass"] is True

    def test_npm_publish_flagged(self):
        result = check_prompt_for_unsafe_instructions("Run npm publish to release the package")
        assert result["pass"] is False


# ---------------------------------------------------------------------------
# quarantine_unsafe_prompt
# ---------------------------------------------------------------------------

class TestQuarantineUnsafePrompt:
    def test_quarantine_writes_file(self, tmp_path):
        p = quarantine_unsafe_prompt("bad prompt text", "unsafe instruction detected", tmp_path)
        assert p.exists()
        content = p.read_text(encoding="utf-8")
        assert "QUARANTINED PROMPT" in content
        assert "bad prompt text" in content


# ---------------------------------------------------------------------------
# validate_product_mutation_evidence
# ---------------------------------------------------------------------------

class TestValidateProductMutationEvidence:
    def test_valid_evidence_no_errors(self):
        from tools.supervisor.autonomy_route_decider import validate_product_mutation_evidence
        ev = {
            "mutation_id": "MUT-001",
            "task_id": "T-001",
            "route_decision_id": "T-001",
            "authorized_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
            "allowed_paths_used": ["src/python/dif/dif_parser.py"],
            "forbidden_paths_checked": ["tools/supervisor/"],
            "tests_proving_mutation": ["tests/python/dif/test_r156.py"],
            "supervisor_verdict_accepted": True,
            "run_id": "test-run",
            "timestamp": "2026-06-10T00:00:00Z",
        }
        errors = validate_product_mutation_evidence(ev)
        assert errors == []

    def test_missing_fields_detected(self):
        from tools.supervisor.autonomy_route_decider import validate_product_mutation_evidence
        errors = validate_product_mutation_evidence({"mutation_id": "X"})
        assert len(errors) >= 5

    def test_empty_tests_rejected(self):
        from tools.supervisor.autonomy_route_decider import validate_product_mutation_evidence
        ev = {
            "mutation_id": "MUT-002",
            "task_id": "T-002",
            "route_decision_id": "T-002",
            "authorized_route": "AUTONOMOUS_ACCELERATED_DEFAULT",
            "allowed_paths_used": ["src/"],
            "forbidden_paths_checked": [],
            "tests_proving_mutation": [],
        }
        errors = validate_product_mutation_evidence(ev)
        assert any("non-empty" in e for e in errors)


# ---------------------------------------------------------------------------
# enrich_work_item_with_route
# ---------------------------------------------------------------------------

class TestEnrichWorkItemWithRoute:
    def test_unknown_summary_marked_advisory(self):
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        item = {"task_id": "T-ENR-001", "task_summary": "xyz unknown task qqq"}
        enriched = enrich_work_item_with_route(item)
        assert enriched["route_status"] == "ADVISORY_ONLY"
        assert enriched["executable"] is False

    def test_product_item_gets_route_decision(self, tmp_path):
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        item = {
            "task_id": "T-ENR-002",
            "task_summary": "Implement ABW function",
            "required_tests": ["t.py"],
            "required_evidence": ["e.json"],
            "allowed_paths": ["src/python/abw/"],
        }
        enriched = enrich_work_item_with_route(item, decisions_dir=tmp_path)
        assert enriched["task_category"] == "PRODUCT_IMPLEMENTATION"
        assert enriched["route_decision_id"] == "T-ENR-002"
        assert enriched["executable"] is True
        # Decision file should exist on disk
        assert (tmp_path / "T-ENR-002.json").exists()

    def test_no_task_id_blocked(self):
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        item = {"task_summary": "Implement something"}
        enriched = enrich_work_item_with_route(item)
        assert enriched["executable"] is False

    def test_existing_route_decision_preserved(self):
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        item = {
            "task_id": "T-ENR-003",
            "task_category": "PRODUCT_IMPLEMENTATION",
            "route_decision_id": "EXISTING-RD",
        }
        enriched = enrich_work_item_with_route(item)
        assert enriched["route_decision_id"] == "EXISTING-RD"
        assert enriched["route_status"] == "PRE_EXISTING"


# ---------------------------------------------------------------------------
# check_action_route_allowed — product source-mutating hardening
# ---------------------------------------------------------------------------

class TestProductSourceMutatingRouteEnforcement:
    def test_product_source_mutating_no_route_decision_blocked(self):
        action = {
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_id": "T-PSM-001",
        }
        allowed, reason = check_action_route_allowed(action)
        assert allowed is False
        assert "route_decision_id" in reason

    def test_product_source_mutating_with_valid_route_allowed(self, tmp_path):
        d = decide_route(
            "T-PSM-002", "PRODUCT_IMPLEMENTATION", "Implement function",
            hints={
                "required_tests": ["t.py"],
                "required_evidence": ["e.json"],
                "allowed_paths": ["src/"],
            },
        )
        d.write(output_dir=tmp_path)

        action = {
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_id": "T-PSM-002",
            "route_decision_id": "T-PSM-002",
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is True

    def test_product_source_mutating_blocked_decision_rejected(self, tmp_path):
        d = decide_route("T-PSM-003", "UNKNOWN_OR_AMBIGUOUS", "Vague")
        d.write(output_dir=tmp_path)

        action = {
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_id": "T-PSM-003",
            "route_decision_id": "T-PSM-003",
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is False

    def test_product_source_mutating_category_mismatch_blocked(self, tmp_path):
        d = decide_route(
            "T-PSM-004", "PRODUCT_TESTING", "Run tests",
            hints={
                "required_tests": ["t.py"],
                "required_evidence": ["e.json"],
                "allowed_paths": ["tests/"],
            },
        )
        d.write(output_dir=tmp_path)

        action = {
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_id": "T-PSM-004",
            "route_decision_id": "T-PSM-004",
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is False
        assert "mismatch" in reason

    def test_product_source_mutating_empty_tests_blocked(self, tmp_path):
        d = decide_route(
            "T-PSM-005", "PRODUCT_IMPLEMENTATION", "Implement",
            hints={
                "required_tests": [],
                "required_evidence": ["e.json"],
                "allowed_paths": ["src/"],
            },
        )
        # Override to get AGENT_GOVERNED route but force write
        d.write(output_dir=tmp_path)

        action = {
            "task_category": "PRODUCT_IMPLEMENTATION",
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "task_id": "T-PSM-005",
            "route_decision_id": "T-PSM-005",
        }
        allowed, reason = check_action_route_allowed(action, decisions_dir=tmp_path)
        assert allowed is False
        assert "required_tests" in reason

    def test_product_non_source_mutating_allowed_without_route(self):
        action = {
            "task_category": "PRODUCT_TESTING",
            "action_type": "RUN_TARGETED_PYTEST",
            "task_id": "T-PSM-006",
        }
        allowed, _ = check_action_route_allowed(action)
        assert allowed is True
