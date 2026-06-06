"""
Tests for next_action_generator.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import json
import pytest
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.next_action_generator import (
    FORBIDDEN_STREAM_ACTIONS,
    SAFE_ACTION_TYPES,
    generate_next_action,
    get_generation_trace,
)

_SPRINT_ID = "FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001"


class TestGenerateNextAction:
    def test_returns_dict_for_cycle_1(self):
        action = generate_next_action(None, 1, _SPRINT_ID)
        assert action is not None
        assert isinstance(action, dict)

    def test_action_has_required_fields(self):
        action = generate_next_action(None, 1, _SPRINT_ID)
        assert "action_id" in action
        assert "action_type" in action
        assert "objective" in action
        assert "preferred_backend" in action

    def test_action_type_is_safe(self):
        for cycle in range(1, 6):
            action = generate_next_action(None, cycle, _SPRINT_ID)
            if action:
                assert action["action_type"] not in FORBIDDEN_STREAM_ACTIONS

    def test_preferred_backend_is_local_deterministic(self):
        action = generate_next_action(None, 1, _SPRINT_ID)
        assert action["preferred_backend"] == "LOCAL_DETERMINISTIC"

    def test_no_external_gate(self):
        for cycle in range(1, 4):
            action = generate_next_action(None, cycle, _SPRINT_ID)
            if action:
                assert not action.get("external_gate", False)

    def test_cycle_2_action_references_prev_result(self):
        prev = {"result_path": "reports/autonomous-orchestrator/proof-run/cycle-001-result.json"}
        action = generate_next_action(prev, 2, _SPRINT_ID)
        assert action is not None
        assert action.get("previous_cycle_result") == prev["result_path"]

    def test_different_cycles_rotate_action_types(self):
        types_seen = set()
        for cycle in range(1, 6):
            action = generate_next_action(None, cycle, _SPRINT_ID)
            if action:
                types_seen.add(action["action_type"])
        assert len(types_seen) >= 2, "Expected at least 2 distinct action types across 5 cycles"

    def test_generation_trace_records_entries(self):
        generate_next_action(None, 10, _SPRINT_ID)
        trace = get_generation_trace()
        assert "entries" in trace
        assert len(trace["entries"]) >= 1

    def test_no_commit_push_in_generated_action(self):
        for cycle in range(1, 5):
            action = generate_next_action(None, cycle, _SPRINT_ID)
            if action:
                desc = str(action.get("objective", "")).lower()
                for kw in ["git commit", "git push", "npm publish", "nuget push"]:
                    assert kw not in desc


class TestForbiddenStreamActions:
    def test_forbidden_set_contains_git_push(self):
        assert "GIT_PUSH" in FORBIDDEN_STREAM_ACTIONS

    def test_forbidden_set_contains_gate_approval(self):
        assert "GATE_8_APPROVAL" in FORBIDDEN_STREAM_ACTIONS
        assert "GATE_11_APPROVAL" in FORBIDDEN_STREAM_ACTIONS

    def test_forbidden_set_contains_package_publish(self):
        assert "PACKAGE_PUBLISH" in FORBIDDEN_STREAM_ACTIONS


class TestSafeActionTypes:
    def test_run_json_validation_is_safe(self):
        assert "RUN_JSON_VALIDATION" in SAFE_ACTION_TYPES

    def test_run_md_check_is_safe(self):
        assert "RUN_MD_NONEMPTY_CHECK" in SAFE_ACTION_TYPES

    def test_run_yaml_validation_is_safe(self):
        assert "RUN_YAML_VALIDATION" in SAFE_ACTION_TYPES
