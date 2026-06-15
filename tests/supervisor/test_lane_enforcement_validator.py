"""Tests for lane enforcement validator — PASS and FAIL cases.

TC-GAP-A04: Proves lane violations produce FAIL verdicts.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.lane_enforcement_validator import LaneEnforcementValidator


class TestLaneEnforcementValidator:
    def test_pass_clean_declaration(self):
        """Declaration with files matching declared lane → PASS."""
        declaration = {
            "changed_files": [
                "src/python/fods/parser.py",
                "tests/python/fods/test_parser.py",
            ]
        }
        result = LaneEnforcementValidator().validate(
            declaration, declared_lane="PYTHON_PRODUCT"
        )
        assert result.passed is True
        assert len(result.violations) == 0
        assert len(result.evidence) >= 2

    def test_fail_cross_lane_violation(self):
        """Declaration editing supervisor files while claiming PYTHON_PRODUCT → FAIL."""
        declaration = {
            "changed_files": [
                "src/python/fods/parser.py",
                "tools/supervisor/governance_validators.py",
            ]
        }
        result = LaneEnforcementValidator().validate(
            declaration, declared_lane="PYTHON_PRODUCT"
        )
        assert result.passed is False
        assert len(result.violations) >= 1
        assert any("SUPERVISOR" in v for v in result.violations)
