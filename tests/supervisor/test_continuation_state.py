"""
Tests for continuation_state.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import json
import pytest
import sys
import tempfile
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.continuation_state import (
    is_advisory_prompt,
    is_action_safe,
    make_active_continuation,
    make_orchestrator_state,
    validate_active_continuation,
    STOP_ADVISORY_PROMPT,
    STOP_MAX_CYCLES,
    STREAM_AUTONOMY,
)


class TestAdvisoryPromptDetection:
    def test_next_sprint_md_is_advisory(self):
        assert is_advisory_prompt("reports/supervisor/next-sprint.md")

    def test_combined_prompt_is_advisory(self):
        assert is_advisory_prompt("reports/supervisor/combined-next-worker-prompt.md")

    def test_any_md_file_is_advisory(self):
        assert is_advisory_prompt("some/path/something.md")

    def test_next_work_items_json_is_advisory(self):
        assert is_advisory_prompt("review/next-work-items.json")

    def test_next_action_json_is_not_advisory(self):
        assert not is_advisory_prompt(".local/supervisor/next-action.json")

    def test_proof_result_json_not_advisory(self):
        assert not is_advisory_prompt("reports/autonomous-orchestrator/proof-run/cycle-001-result.json")


class TestActionSafety:
    def test_run_json_validation_is_safe(self):
        action = {"action_type": "RUN_JSON_VALIDATION", "description": "validate a file"}
        safe, reason = is_action_safe(action)
        assert safe

    def test_git_push_is_forbidden(self):
        action = {"action_type": "GIT_PUSH", "description": "push changes"}
        safe, reason = is_action_safe(action)
        assert not safe
        assert "GIT_PUSH" in reason

    def test_gate_11_approval_is_forbidden(self):
        action = {"action_type": "GATE_11_APPROVAL", "description": "approve gate"}
        safe, reason = is_action_safe(action)
        assert not safe

    def test_external_gate_true_is_unsafe(self):
        action = {"action_type": "RUN_JSON_VALIDATION", "external_gate": True, "description": ""}
        safe, reason = is_action_safe(action)
        assert not safe

    def test_commit_keyword_in_description_is_unsafe(self):
        action = {"action_type": "RUN_COMMAND_DISCOVERY", "description": "git commit the results"}
        safe, reason = is_action_safe(action)
        assert not safe

    def test_package_publish_is_forbidden(self):
        action = {"action_type": "PACKAGE_PUBLISH"}
        safe, _ = is_action_safe(action)
        assert not safe


class TestActiveContinuationValidation:
    def test_valid_continuation(self, tmp_path):
        # Create a valid next-action file
        nap = tmp_path / "next-action.json"
        nap.write_text('{"action_id":"t1","action_type":"RUN_JSON_VALIDATION","objective":"test","preferred_backend":"LOCAL_DETERMINISTIC"}')
        cont = {
            "autonomous_continue": True,
            "next_action_path": str(nap),
            "advisory_prompt_executable": False,
        }
        errors = validate_active_continuation(cont)
        assert errors == []

    def test_autonomous_continue_true_missing_next_action_path_fails(self):
        cont = {"autonomous_continue": True, "next_action_path": "", "advisory_prompt_executable": False}
        errors = validate_active_continuation(cont)
        assert any("next_action_path" in e for e in errors)

    def test_advisory_prompt_executable_true_fails(self):
        cont = {"autonomous_continue": False, "advisory_prompt_executable": True}
        errors = validate_active_continuation(cont)
        assert any("advisory_prompt_executable" in e for e in errors)

    def test_next_action_pointing_to_md_fails(self):
        cont = {
            "autonomous_continue": True,
            "next_action_path": "reports/supervisor/next-sprint.md",
            "advisory_prompt_executable": False,
        }
        errors = validate_active_continuation(cont)
        assert any("advisory prompt" in e for e in errors)

    def test_autonomous_continue_false_with_missing_path_ok(self):
        cont = {"autonomous_continue": False, "advisory_prompt_executable": False}
        errors = validate_active_continuation(cont)
        assert errors == []


class TestMakeActiveContinuation:
    def test_make_continuation_has_required_fields(self):
        cont = make_active_continuation(
            source_sprint_id="TEST-001",
            proof_level="H4_PLUS",
            next_action_path=".local/supervisor/next-action.json",
        )
        assert cont["schema_version"] == 1
        assert cont["active_stream"] == STREAM_AUTONOMY
        assert cont["advisory_prompt_executable"] is False
        assert cont["unsafe_advisory_prompts_quarantined"] is True
        assert cont["autonomous_continue"] is True

    def test_make_orchestrator_state_has_resume_supported(self):
        state = make_orchestrator_state("run-123")
        assert state["resume_supported"] is True
        assert state["status"] == "RUNNING"
        assert state["cycle_index"] == 0
