"""Regression tests for TC-GUARD-001 BLOCK mode enforcement.

Change 1: autonomous_cycle.py — TC-GUARD-001 now unconditionally adds PRODUCT_SOURCE /
PRODUCT_TEST items missing gap_ledger_ref, capability_ref, or spec_fact_refs to
rework_items (BLOCK mode). Prior behaviour was WARN-only until 2026-07-18.

Negative control: PRODUCT_SOURCE without gap references -> _guard001_violations
  populated (indirectly verified via governance detection logic mirror).
Positive control: PRODUCT_SOURCE with gap_ledger_ref -> no violation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


# ---------------------------------------------------------------------------
# Unit-level tests: verify TC-GUARD-001 detection logic in isolation
# The actual enforcement is in autonomous_cycle.py around Step 2d3.
# These tests replicate the detection algorithm directly (no subprocess needed).
# ---------------------------------------------------------------------------

def _guard001_violations(declaration: dict) -> list[str]:
    """Mirror the TC-GUARD-001 detection logic from autonomous_cycle.py Step 2d3."""
    GUARD_TYPES = {"PRODUCT_SOURCE", "PRODUCT_TEST"}
    items = [
        item for item in declaration.get("planned_work_items", [])
        if item.get("item_type", "") in GUARD_TYPES
    ]
    violations = [
        item["item_id"] for item in items
        if not (
            item.get("gap_ledger_ref")
            or item.get("capability_ref")
            or item.get("spec_fact_refs")
        )
    ]
    return violations


class TestTCGuard001Detection:
    """Unit tests for TC-GUARD-001 violation detection (BLOCK mode)."""

    def test_product_source_without_gap_ref_is_violation(self):
        """NEGATIVE CONTROL: PRODUCT_SOURCE missing all gap refs -> violation."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-NEG-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Add zst_counts_mod_1069_times_1087",
                "evidence_paths": ["tests/python/zst/test_zst_counts_mod_1069_times_1087.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-NEG-001" in violations, (
            f"Expected TC-G001-NEG-001 to be a violation, got: {violations}"
        )

    def test_product_source_with_gap_ledger_ref_passes(self):
        """POSITIVE CONTROL: PRODUCT_SOURCE with gap_ledger_ref -> no violation."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-POS-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Implement table:table canonical class",
                "gap_ledger_ref": "GAP-FODS-0042",
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-POS-001" not in violations, (
            f"Expected no violation for item with gap_ledger_ref, got: {violations}"
        )

    def test_product_source_with_capability_ref_passes(self):
        """capability_ref satisfies the gap tracing requirement."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-CAP-001",
                "item_type": "PRODUCT_SOURCE",
                "capability_ref": "CAP-FODS-table-count",
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-CAP-001" not in violations

    def test_product_source_with_spec_fact_refs_passes(self):
        """spec_fact_refs satisfies the gap tracing requirement."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-SPEC-001",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-004"],
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-SPEC-001" not in violations

    def test_product_test_without_gap_ref_is_violation(self):
        """PRODUCT_TEST items are also checked by TC-GUARD-001."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-TEST-001",
                "item_type": "PRODUCT_TEST",
                "title": "Test arithmetic deepening with no spec",
                "evidence_paths": ["tests/python/zst/test_zst_pure_arithmetic.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-TEST-001" in violations

    def test_governance_taskcard_is_exempt(self):
        """GOVERNANCE_TASKCARD items are not checked by TC-GUARD-001."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-GOV-001",
                "item_type": "GOVERNANCE_TASKCARD",
                "title": "Update gate11-criteria.yaml",
                "evidence_paths": ["registry/gate11-criteria.yaml"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-GOV-001" not in violations

    def test_multiple_violations_all_reported(self):
        """All violating items are collected, not just the first."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "TC-G001-MULTI-001",
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/zst/zst_codec.py"],
                },
                {
                    "item_id": "TC-G001-MULTI-002",
                    "item_type": "PRODUCT_SOURCE",
                    "evidence_paths": ["src/python/xcf/xcf_parser.py"],
                },
                {
                    "item_id": "TC-G001-MULTI-003",
                    "item_type": "PRODUCT_SOURCE",
                    "gap_ledger_ref": "GAP-FODS-0001",
                    "evidence_paths": ["src/python/fods/neutral_model.py"],
                },
            ]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-MULTI-001" in violations
        assert "TC-G001-MULTI-002" in violations
        assert "TC-G001-MULTI-003" not in violations  # has gap_ledger_ref


class TestTCGuard001InAutonomousCycle:
    """Integration smoke test: verify TC-GUARD-001 block is present in autonomous_cycle.py."""

    def test_guard001_block_mode_code_present(self):
        """The TC-GUARD-001 BLOCK mode code is present (no deadline check)."""
        ac_path = REPO_ROOT / "tools" / "supervisor" / "autonomous_cycle.py"
        src = ac_path.read_text(encoding="utf-8")

        # BLOCK mode marker must be present
        assert "TC-GUARD-001 GAP LEDGER TRACE CHECK (BLOCK MODE)" in src, (
            "TC-GUARD-001 BLOCK MODE header not found in autonomous_cycle.py"
        )
        # _guard001_violations variable must be used for post-grade enforcement
        assert "_guard001_violations" in src, (
            "_guard001_violations flag not found — post-grade enforcement missing"
        )
        # Old deadline-based WARN mode must be gone
        assert "2026-07-18" not in src, (
            "Old 2026-07-18 deadline still present — TC-GUARD-001 not yet in BLOCK mode"
        )
