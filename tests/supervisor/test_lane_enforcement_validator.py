"""Tests for lane enforcement validator — PASS and FAIL cases.

TC-GAP-A04: Proves lane violations produce FAIL verdicts.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.lane_enforcement_validator import (
    LaneEnforcementValidator,
    GLOBAL_EXEMPT_PATHS,
)


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


class TestGlobalExemptPaths:
    """Regression tests for GLOBAL_EXEMPT_PATHS — TC-PHF-001."""

    def test_exempt_paths_defined(self):
        """GLOBAL_EXEMPT_PATHS must include the standard bookkeeping files."""
        assert any("gap-ledger.json" in p for p in GLOBAL_EXEMPT_PATHS)
        assert any("source-structure-baseline.json" in p for p in GLOBAL_EXEMPT_PATHS)
        assert any("product-code-change-ledger.json" in p for p in GLOBAL_EXEMPT_PATHS)

    def test_three_lane_with_only_exempt_cross_lane_files_passes(self):
        """A 3-lane declaration where the cross-lane files are exempt → PASS.

        This is the exact scenario from TOML R120: src/ (PYTHON_PRODUCT) +
        reports/capability-layer/gap-ledger.json (REPORTING, exempt) +
        registry/source-structure-baseline.json (GOVERNANCE, exempt).
        """
        declaration = {
            "changed_files": [
                "src/python/toml/config_document.py",
                "tests/python/toml_format/test_r120_toml_gap_closure.py",
                "reports/capability-layer/gap-ledger.json",
                "registry/source-structure-baseline.json",
            ]
        }
        result = LaneEnforcementValidator().validate(declaration, declared_lane=None)
        assert result.passed is True, f"Expected PASS but got FAIL: {result.violations}"

    def test_three_lane_with_real_cross_lane_product_files_fails(self):
        """A 3-lane declaration with actual cross-lane product edits → FAIL.

        Touching src/python/ + src/net/ + tools/supervisor/ without a lane
        is a genuine violation even if some files are exempt.
        """
        declaration = {
            "changed_files": [
                "src/python/fods/parser.py",
                "src/net/fods/FodsDocument.cs",
                "tools/supervisor/governance_validators.py",
                "reports/capability-layer/gap-ledger.json",  # exempt
            ]
        }
        result = LaneEnforcementValidator().validate(declaration, declared_lane=None)
        assert result.passed is False, "Expected FAIL for genuine cross-lane spread"
        assert len(result.violations) >= 1

    def test_exempt_file_does_not_trigger_declared_lane_violation(self):
        """Exempt file outside declared lane must not produce a cross-lane violation."""
        declaration = {
            "changed_files": [
                "src/python/toml/config_document.py",
                "reports/capability-layer/gap-ledger.json",  # REPORTING, but exempt
                "registry/source-structure-baseline.json",   # GOVERNANCE, but exempt
            ]
        }
        result = LaneEnforcementValidator().validate(
            declaration, declared_lane="PYTHON_PRODUCT"
        )
        assert result.passed is True, f"Exempt files must not trigger violations: {result.violations}"

    def test_resolve_lane_returns_none_for_exempt(self):
        """_resolve_lane returns None for all globally exempt paths."""
        v = LaneEnforcementValidator()
        assert v._resolve_lane("reports/capability-layer/gap-ledger.json") is None
        assert v._resolve_lane("registry/source-structure-baseline.json") is None
        assert v._resolve_lane("reports/r90/product-code-change-ledger.json") is None
        assert v._resolve_lane("reports/supervisor/approval-gates.md") is None
        assert v._resolve_lane(".local/supervisor/continuation-signal.json") is None
        # .supervisor/ files (context-pack, skill-registry) are also exempt
        assert v._resolve_lane(".supervisor/context-pack.yaml") is None
        assert v._resolve_lane(".supervisor/skill-registry.yaml") is None

    def test_non_exempt_reporting_file_still_counts_as_lane(self):
        """A reports/ file that is NOT in GLOBAL_EXEMPT_PATHS is exempt via prefix.

        Note: reports/ maps to REPORTING lane via DEFAULT_LANE_OWNERSHIP, but
        reports/supervisor/ and .local/ are also in GLOBAL_EXEMPT_PATHS.
        A reports/capability-layer/ file other than gap-ledger.json should still
        be exempt (prefix match on reports/supervisor/ does NOT apply).
        We verify that non-exempt report files do resolve to REPORTING.
        """
        v = LaneEnforcementValidator()
        # reports/capability-layer/capability_summary.json is NOT in exempt list
        # It matches reports/ prefix → REPORTING lane
        lane = v._resolve_lane("reports/capability-layer/capability_summary.json")
        assert lane == "REPORTING"


class TestMultiLaneDeclaration:
    """Tests for multi-lane sprint declarations (TC-S55-003)."""

    def test_multi_lane_passes_with_cross_lane_files(self):
        """Declaring MULTI_LANE skips single-lane constraint — multi-format sprints PASS.

        TC-S55-003: sprint declarations for multi-lane work must use declared_scope: multi_lane
        to avoid LANE_ENFORCEMENT violations.
        """
        declaration = {
            "changed_files": [
                "src/python/fods/parser.py",
                "tools/supervisor/governance_validators.py",
                "reports/supervisor/next-sprint.md",
            ]
        }
        result = LaneEnforcementValidator().validate(
            declaration, declared_lane="MULTI_LANE"
        )
        assert result.passed is True, f"MULTI_LANE declaration should PASS: {result.violations}"
        assert len(result.violations) == 0
        assert any("Multi-lane" in e or "multi" in e.lower() for e in result.evidence)

    def test_multi_lane_case_insensitive(self):
        """declared_lane='multi_lane' (lowercase) is accepted as MULTI_LANE."""
        declaration = {
            "changed_files": [
                "src/python/xcf/xcf_parser.py",
                "src/net/fods/FodsDocument.cs",
            ]
        }
        result = LaneEnforcementValidator().validate(
            declaration, declared_lane="multi_lane"
        )
        assert result.passed is True

    def test_single_lane_cross_lane_still_fails(self):
        """Without MULTI_LANE declared, cross-lane spread still produces violations."""
        declaration = {
            "changed_files": [
                "src/python/fods/parser.py",
                "tools/supervisor/governance_validators.py",
            ]
        }
        result = LaneEnforcementValidator().validate(
            declaration, declared_lane="PYTHON_PRODUCT"
        )
        assert result.passed is False, "Cross-lane without MULTI_LANE should FAIL"
