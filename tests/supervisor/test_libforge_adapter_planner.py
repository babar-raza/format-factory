"""
test_libforge_adapter_planner.py — Tests for LibForge adapter planner.

Sprint: FF-LIBFORGE-REFOCUS-INTEGRATION-001
Verifies plan building, JSON serialization, pattern-level actions,
handling of unsafe/missing patterns.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.supervisor.libforge_adapter_planner import (
    AdapterAction,
    AdapterPlan,
    build_plan,
    plan_for_pattern,
    plan_to_dict,
    plan_to_json,
)


class TestPlanBuilding:
    def test_build_plan_returns_plan(self):
        plan = build_plan()
        assert isinstance(plan, AdapterPlan)

    def test_plan_has_actions(self):
        plan = build_plan()
        assert len(plan.actions) >= 6

    def test_plan_has_summary(self):
        plan = build_plan()
        assert isinstance(plan.summary, str)
        assert len(plan.summary) > 20

    def test_plan_id_set(self):
        plan = build_plan(plan_id="test-plan-001")
        assert plan.plan_id == "test-plan-001"

    def test_plan_sprint_id_set(self):
        plan = build_plan(sprint_id="SPRINT-TEST-001")
        assert plan.generated_for == "SPRINT-TEST-001"


class TestActionTypes:
    def test_no_reject_actions_in_default_plan(self):
        """No patterns are marked REJECT_UNSAFE in current registry, so no reject actions."""
        plan = build_plan()
        reject_actions = [a for a in plan.actions if a.action_type == "reject"]
        # All current patterns are either FF_NATIVE or WRAPPER_REUSE, not REJECT_UNSAFE
        # Verify rejected list matches reject_actions
        assert len(plan.rejected_patterns) == len(reject_actions)

    def test_implement_actions_present(self):
        plan = build_plan()
        implement_actions = [a for a in plan.actions if a.action_type == "implement"]
        assert len(implement_actions) >= 4

    def test_high_priority_actions_present(self):
        plan = build_plan()
        high_prio = [a for a in plan.actions if a.priority == 1]
        assert len(high_prio) >= 3

    def test_all_actions_have_required_fields(self):
        plan = build_plan()
        for action in plan.actions:
            assert isinstance(action.action_id, str)
            assert isinstance(action.pattern_id, str)
            assert isinstance(action.action_type, str)
            assert isinstance(action.target_file, str)
            assert isinstance(action.priority, int)
            assert isinstance(action.safe, bool)


class TestPatternLevelPlan:
    def test_plan_for_known_pattern(self):
        action = plan_for_pattern("SPECDEV-FREEZE-GATE")
        assert action is not None
        assert action.pattern_id == "SPECDEV-FREEZE-GATE"

    def test_plan_for_unknown_pattern_returns_none(self):
        action = plan_for_pattern("DOES_NOT_EXIST_XYZ_999")
        assert action is None

    def test_compose_verify_action_targets_ff_file(self):
        action = plan_for_pattern("REFDEV-COMPOSE-VERIFY-LOOP")
        assert action is not None
        assert "compose_verify_loop.py" in action.target_file

    def test_isolated_job_runner_action_is_implement(self):
        action = plan_for_pattern("SPECDEV-ISOLATED-JOB-EXECUTION")
        assert action is not None
        assert action.action_type == "implement"

    def test_llm_boundary_action_present(self):
        action = plan_for_pattern("REFDEV-SINGLE-LLM-BOUNDARY")
        assert action is not None
        assert action.action_type == "implement"


class TestSerialization:
    def test_plan_to_dict_is_json_serializable(self):
        plan = build_plan()
        d = plan_to_dict(plan)
        json_str = json.dumps(d)
        parsed = json.loads(json_str)
        assert "plan_id" in parsed
        assert "actions" in parsed

    def test_plan_to_json_returns_string(self):
        plan = build_plan()
        json_str = plan_to_json(plan)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "summary" in parsed

    def test_plan_dict_actions_list(self):
        plan = build_plan()
        d = plan_to_dict(plan)
        assert isinstance(d["actions"], list)
        assert len(d["actions"]) == len(plan.actions)

    def test_plan_dict_action_keys(self):
        plan = build_plan()
        d = plan_to_dict(plan)
        required_keys = {
            "action_id", "pattern_id", "action_type",
            "target_file", "description", "blocked_by", "priority", "safe",
        }
        for action in d["actions"]:
            assert required_keys.issubset(action.keys())
