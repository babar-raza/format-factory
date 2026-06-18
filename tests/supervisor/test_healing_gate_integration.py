"""V4: System healing gate integration tests (Design 4 / Phase B).

Verifies check_healing_gate() programmatic API:
1. Returns expected keys in result dict
2. advisory=True means blocks_sprint is always False regardless of exit_code
3. advisory=False means blocks_sprint reflects exit_code
4. evaluate_gate() produces valid exit codes (0, 1, or 2)
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools/supervisor"))

from check_system_healing_gate import check_healing_gate, evaluate_gate  # noqa: E402


class TestCheckHealingGateAPI:
    def test_returns_required_keys(self):
        """check_healing_gate() result contains all expected keys."""
        result = check_healing_gate(advisory=True)
        required = {"exit_code", "verdict", "critical_passed", "all_passed",
                    "failed_lanes", "lane_results", "advisory", "blocks_sprint"}
        assert required.issubset(result.keys())

    def test_advisory_true_never_blocks(self):
        """In advisory mode (default), blocks_sprint is always False."""
        # Force a failing gate by patching evaluate_gate to return failing result
        failing_result = {
            "verdict": "FAILED",
            "exit_code": 1,
            "all_passed": False,
            "critical_passed": False,
            "failed_lanes": [1, 3, 5],
            "lane_results": [],
        }
        with patch("check_system_healing_gate.evaluate_gate", return_value=failing_result):
            result = check_healing_gate(advisory=True)
        assert result["blocks_sprint"] is False
        assert result["advisory"] is True

    def test_advisory_false_blocks_on_failure(self):
        """In strict mode, blocks_sprint=True when exit_code != 0."""
        failing_result = {
            "verdict": "FAILED",
            "exit_code": 1,
            "all_passed": False,
            "critical_passed": False,
            "failed_lanes": [1],
            "lane_results": [],
        }
        with patch("check_system_healing_gate.evaluate_gate", return_value=failing_result):
            result = check_healing_gate(advisory=False)
        assert result["blocks_sprint"] is True
        assert result["advisory"] is False

    def test_advisory_false_no_block_on_pass(self):
        """In strict mode, blocks_sprint=False when exit_code == 0."""
        passing_result = {
            "verdict": "PASSED",
            "exit_code": 0,
            "all_passed": True,
            "critical_passed": True,
            "failed_lanes": [],
            "lane_results": [],
        }
        with patch("check_system_healing_gate.evaluate_gate", return_value=passing_result):
            result = check_healing_gate(advisory=False)
        assert result["blocks_sprint"] is False

    def test_conditional_advisory_does_not_block(self):
        """CONDITIONAL verdict (exit_code=2) still does not block in advisory mode."""
        conditional_result = {
            "verdict": "CONDITIONAL",
            "exit_code": 2,
            "all_passed": False,
            "critical_passed": True,
            "failed_lanes": [2, 6],
            "lane_results": [],
        }
        with patch("check_system_healing_gate.evaluate_gate", return_value=conditional_result):
            result = check_healing_gate(advisory=True)
        assert result["blocks_sprint"] is False

    def test_evaluate_gate_exit_codes_valid(self):
        """evaluate_gate() returns a valid exit code (0, 1, or 2)."""
        result = evaluate_gate()
        assert result["exit_code"] in (0, 1, 2)
        assert result["verdict"] in ("PASSED", "FAILED", "CONDITIONAL")

    def test_evaluate_gate_lane_results_present(self):
        """evaluate_gate() returns non-empty lane_results list."""
        result = evaluate_gate()
        assert isinstance(result["lane_results"], list)
        assert len(result["lane_results"]) > 0

    def test_check_healing_gate_default_advisory(self):
        """Default call is advisory=True."""
        result = check_healing_gate()
        assert result["advisory"] is True
