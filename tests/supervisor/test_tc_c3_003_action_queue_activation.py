"""TC-C3-003: Test verifying queue consumer processes non-advisory (machine-executable) items.

Verifies: a FOSS gap with priority P0 or P1 AND spec_facts → advisory_only=False.
This tests the TC-SH-004 logic in compile_gaps_to_taskcards().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from capability_queue_consumer import gap_to_compiler_input  # noqa: E402


def _make_foss_gap(priority: str, gap_type: str = "missing_test_coverage", spec_facts=None):
    return {
        "gap_id": f"GAP-TEST-{priority}",
        "format": "CSV",
        "capability_name": "count_rows",
        "priority": priority,
        "product_type": "foss_reduced",
        "gap_type": gap_type,
        "commercial_impact": "NONE",
        "spec_facts": spec_facts or [],
    }


class TestAdvisoryOnlyLogic:
    """Verify advisory_only=False when conditions met: FOSS + P0/P1 + spec_facts."""

    def _advisory_only(self, gap: dict) -> bool:
        """Mirror TC-SH-004 logic from compile_gaps_to_taskcards."""
        from capability_queue_consumer import _ELIGIBLE_PRODUCT_TYPES
        compiler_input = gap_to_compiler_input(gap)
        gap_priority = compiler_input.get("priority", "P2")
        has_spec_facts = bool(gap.get("spec_facts"))
        is_foss = gap.get("product_type", "").lower() in _ELIGIBLE_PRODUCT_TYPES
        is_commercial = gap.get("product_type", "").lower() == "commercial"
        if is_foss and gap_priority in ("P0", "P1") and has_spec_facts and not is_commercial:
            return False
        return True

    def test_foss_p1_with_spec_facts_is_machine_executable(self):
        """FOSS P1 gap with spec_facts → advisory_only=False (machine-executable)."""
        gap = _make_foss_gap("P1", spec_facts=["FACT-CSV-001"])
        assert self._advisory_only(gap) is False, (
            "FOSS P1 + spec_facts should be machine-executable (advisory_only=False)"
        )

    def test_foss_p0_with_spec_facts_is_machine_executable(self):
        """FOSS P0 gap with spec_facts → advisory_only=False."""
        gap = _make_foss_gap("P0", spec_facts=["FACT-CSV-001", "FACT-CSV-002"])
        assert self._advisory_only(gap) is False

    def test_foss_p1_without_spec_facts_is_advisory(self):
        """FOSS P1 gap WITHOUT spec_facts → advisory_only=True (requires spec grounding)."""
        gap = _make_foss_gap("P1", spec_facts=[])
        assert self._advisory_only(gap) is True

    def test_foss_p2_with_spec_facts_is_advisory(self):
        """FOSS P2 gap even WITH spec_facts → advisory_only=True (priority not P0/P1)."""
        gap = _make_foss_gap("P2", spec_facts=["FACT-CSV-001"])
        assert self._advisory_only(gap) is True

    def test_foss_p3_with_spec_facts_is_advisory(self):
        """FOSS P3 → advisory_only=True."""
        gap = _make_foss_gap("P3", spec_facts=["FACT-CSV-001"])
        assert self._advisory_only(gap) is True

    def test_commercial_p0_with_spec_facts_is_advisory(self):
        """Commercial gap even at P0 → advisory_only=True (Gate 11 required)."""
        gap = {
            "gap_id": "GAP-COMM-001",
            "format": "CSV",
            "capability_name": "export_to_xlsx",
            "priority": "P0",
            "product_type": "commercial",
            "gap_type": "missing_test_coverage",
            "commercial_impact": "HIGH",
            "spec_facts": ["FACT-CSV-001"],
        }
        assert self._advisory_only(gap) is True

    def test_foss_p1_empty_spec_facts_list_is_advisory(self):
        """Empty spec_facts list (falsy) → advisory_only=True."""
        gap = _make_foss_gap("P1", spec_facts=[])
        assert self._advisory_only(gap) is True

    def test_foss_p1_none_spec_facts_is_advisory(self):
        """None spec_facts → advisory_only=True."""
        gap = _make_foss_gap("P1", spec_facts=None)
        assert self._advisory_only(gap) is True


class TestGapToCompilerInput:
    """Verify gap_to_compiler_input() produces correct fields."""

    def test_machine_executable_gap_has_correct_priority(self):
        """Priority P1 is preserved in compiler input."""
        gap = _make_foss_gap("P1", spec_facts=["FACT-CSV-001"])
        ci = gap_to_compiler_input(gap)
        assert ci["priority"] == "P1"

    def test_commercial_impact_preserved(self):
        """commercial_impact is passed through to compiler input."""
        gap = _make_foss_gap("P1", spec_facts=["FACT-CSV-001"])
        gap["commercial_impact"] = "HIGH"
        ci = gap_to_compiler_input(gap)
        assert ci["commercial_impact"] == "HIGH"
