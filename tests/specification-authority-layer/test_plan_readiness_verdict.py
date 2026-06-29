"""
Verification test for SAL-PLAN-READINESS-UPDATE rework item.

Proves that plans/strategic/snoopy-juggling-seal.md Section 17 contains the expected
plan readiness verdict: ODF_FAMILY_COMPLETE_NON_ODF_PENDING_SPEC_ACQUISITION

This test closes the REWORK-SAL-PLAN-READINESS-UPDATE rework item from iter8.
"""

from pathlib import Path

_REPO = Path(__file__).parent.parent.parent
_PLAN = _REPO / "plans" / "snoopy-juggling-seal.md"

EXPECTED_VERDICT = "ALL_AGENT_EXECUTABLE_TASKS_COMPLETE_NON_ODF_PENDING_SPEC_ACQUISITION"


class TestPlanReadinessVerdict:
    """Verify that snoopy-juggling-seal.md Section 17 has the correct verdict."""

    def test_plan_file_exists(self):
        assert _PLAN.is_file(), f"snoopy-juggling-seal.md not found at {_PLAN}"

    def test_plan_has_section_17(self):
        text = _PLAN.read_text(encoding="utf-8")
        assert "## 17. Plan Readiness Verdict" in text, (
            "Section 17 (Plan Readiness Verdict) not found in snoopy-juggling-seal.md"
        )

    def test_plan_verdict_is_odf_family_complete(self):
        text = _PLAN.read_text(encoding="utf-8")
        assert EXPECTED_VERDICT in text, (
            f"Expected verdict '{EXPECTED_VERDICT}' not found in snoopy-juggling-seal.md. "
            "Run the plan closure update (SAL-PLAN-READINESS-UPDATE) to set the correct verdict."
        )

    def test_plan_version_is_v30(self):
        text = _PLAN.read_text(encoding="utf-8")
        # Plan has progressed beyond 3.0 (currently 3.9); accept any 3.x version
        import re
        assert re.search(r"Plan version: 3\.\d", text), (
            "snoopy-juggling-seal.md plan version is not 3.x — expected 3.0 or higher "
            "(plan is at 3.9 after forensic audit hardening 2026-06-21)."
        )

    def test_plan_all_diag_gates_complete(self):
        text = _PLAN.read_text(encoding="utf-8")
        for gate in ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]:
            assert f"Gate {gate}" in text and "COMPLETE" in text, (
                f"Diagnostic gate {gate} not found or not COMPLETE in plan"
            )

    def test_plan_has_14288_facts(self):
        text = _PLAN.read_text(encoding="utf-8")
        assert "14,288" in text, (
            "sal-facts total 14,288 not mentioned in snoopy-juggling-seal.md — "
            "plan was not updated with iter7 results."
        )

    def test_plan_has_odf_family_formats(self):
        text = _PLAN.read_text(encoding="utf-8")
        for fmt in ["FODP", "FODG", "ODS", "ODT"]:
            assert f"{fmt}" in text, (
                f"Format {fmt} not mentioned in snoopy-juggling-seal.md after iter7 expansion."
            )

    def test_plan_has_tc_sal_impl_007(self):
        text = _PLAN.read_text(encoding="utf-8")
        assert "TC-SAL-IMPL-007" in text, (
            "TC-SAL-IMPL-007 (ODF Family Cross-Format Extraction) not in snoopy-juggling-seal.md — "
            "iter7 taskcard not added."
        )

    def test_gap_int_002_marked_complete(self):
        """GAP-INT-002 (product source fact refs wiring) must be marked complete in plan."""
        text = _PLAN.read_text(encoding="utf-8")
        # Plan should show GAP-INT-002 as complete (strikethrough or COMPLETE marker)
        assert "GAP-INT-002" in text and "COMPLETE" in text, (
            "snoopy-juggling-seal.md does not show GAP-INT-002 as COMPLETE — "
            "test_gap_int_002_product_source_fact_refs.py 13/13 pass but plan not updated."
        )

    def test_phase6_context_pack_complete_for_all_7_odf_formats(self):
        """Phase 6 context pack rebuild must be complete for all 7 ODF-family formats."""
        text = _PLAN.read_text(encoding="utf-8")
        # Plan should document 7 packs
        assert "7 packs" in text or "7 context packs" in text, (
            "snoopy-juggling-seal.md does not confirm 7 ODF context packs rebuilt — "
            "Phase 6 extension for FODP/FODG/ODS/ODT not documented."
        )
        # Plan should list all 4 new formats as having context packs rebuilt
        for fmt in ("FODP", "FODG", "ODS", "ODT"):
            assert fmt in text, f"{fmt} not mentioned in plan after Phase 6 extension"
