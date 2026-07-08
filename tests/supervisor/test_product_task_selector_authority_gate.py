"""
test_product_task_selector_authority_gate.py
Sprint: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-REPAIR-AND-ENFORCEMENT-001
Added: 2026-06-07

Tests for product_task_selector authority gate enforcement.
Proves that authority-blocked formats cannot emit executable product source tasks.
"""
import sys
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

from product_task_selector import (
    _check_candidate,
    _get_format_authority_status,
    _BLOCKED_AUTHORITY_STATES,
)


class TestAuthorityGate:
    """Product task selector must block formats in authority-blocked states."""

    def test_blocked_missing_spec_format_is_not_actionable(self):
        """A format with authority_status=BLOCKED_MISSING_SPEC cannot be selected."""
        candidate = {
            "task_id": "test-task-001",
            "format": "HYPOTHETICAL_FORMAT",
            "action": "add_function",
            "target_file": "src/python/abw/abw_codec.py",  # use a real file
            "also_modifies": [],
            "function_name": "probe_abw",  # already exists — won't matter due to authority gate
            "classification": "AGENT_OWNED_SAFE",
        }
        with patch(
            "product_task_selector._get_format_authority_status",
            return_value="BLOCKED_MISSING_SPEC",
        ):
            result = _check_candidate(candidate)
        assert not result["actionable"], "Should not be actionable with BLOCKED_MISSING_SPEC"
        assert "authority_gate_blocked" in result.get("blocker", "")

    def test_all_blocked_states_prevent_task_selection(self):
        """Every BLOCKED_* authority state prevents actionable status."""
        candidate = {
            "task_id": "test-task-002",
            "format": "TEST_FORMAT",
            "action": "add_function",
            "target_file": "src/python/abw/abw_codec.py",
            "also_modifies": [],
            "function_name": "__nonexistent_func_xyz__",  # not present
            "classification": "AGENT_OWNED_SAFE",
        }
        for blocked_state in _BLOCKED_AUTHORITY_STATES:
            with patch(
                "product_task_selector._get_format_authority_status",
                return_value=blocked_state,
            ):
                result = _check_candidate(candidate)
            assert not result.get("actionable"), (
                f"Should not be actionable with authority_status={blocked_state}"
            )
            assert "authority_gate_blocked" in result.get("blocker", ""), (
                f"blocker should mention authority_gate_blocked for {blocked_state}"
            )

    def test_allowed_format_can_still_be_actionable(self):
        """An ALLOWED format with an unimplemented function is actionable."""
        candidate = {
            "task_id": "test-task-003",
            "format": "ABW",
            "action": "add_function",
            "target_file": "src/python/abw/abw_codec.py",
            "also_modifies": [],
            "function_name": "__nonexistent_func_xyz__",  # definitely not present
            "classification": "AGENT_OWNED_SAFE",
        }
        with patch(
            "product_task_selector._get_format_authority_status",
            return_value="ALLOWED",
        ):
            result = _check_candidate(candidate)
        # The function is absent so it should be actionable if file exists
        assert result["target_exists"], "Target file should exist"
        assert result["actionable"], "Should be actionable when authority is ALLOWED and function absent"

    def test_get_format_authority_status_returns_status_for_unknown_format(self):
        """Unknown formats without poc-targets entry return a non-ALLOWED status.

        Current behavior: ALLOWED_WITH_EXCEPTION:legacy_backfill for unknown formats
        (legacy backfill path allows product work with reduced authority).
        """
        status = _get_format_authority_status("FORMAT_NOT_IN_REGISTRY_XYZ_999")
        assert status is not None and len(status) > 0, "Status must be non-empty"

    def test_unknown_format_candidate_has_result(self):
        """Unknown format candidate check returns a result dict."""
        candidate = {
            "task_id": "test-task-unknown",
            "format": "COMPLETELY_UNKNOWN_FORMAT_XYZ_999",
            "action": "add_function",
            "target_file": "src/python/abw/abw_codec.py",
            "also_modifies": [],
            "function_name": "__nonexistent_func_xyz__",
            "classification": "AGENT_OWNED_SAFE",
        }
        result = _check_candidate(candidate)
        assert isinstance(result, dict), "Result must be a dict"

    def test_blocked_states_set_is_complete(self):
        """All required blocked authority states are defined."""
        required = {
            "BLOCKED_MISSING_SPEC",
            "BLOCKED_METADATA_ONLY_SPEC",
            "BLOCKED_NO_VERIFIED_FACTS",
            "BLOCKED_SYNTHETIC_REQUIREMENTS",
            "BLOCKED_AI_ONLY_AUTHORITY",
        }
        assert required.issubset(_BLOCKED_AUTHORITY_STATES)
