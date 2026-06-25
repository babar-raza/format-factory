"""Regression tests for TC-GUARD-001 BLOCK mode enforcement.

Change 1: autonomous_cycle.py — TC-GUARD-001 now unconditionally adds PRODUCT_SOURCE /
PRODUCT_TEST items missing gap_ledger_ref, capability_ref, or spec_fact_refs to
rework_items (BLOCK mode). Prior behaviour was WARN-only until 2026-07-18.

Change 2 (SAL-HEAL-A001, 2026-06-25): TC-GUARD-001 now requires AND logic:
  (gap_ledger_ref OR capability_ref) AND (spec_fact_refs OR exception_classification)
  gap_ledger_ref alone is no longer sufficient. Spec authority citation is also required.

Negative controls:
  - No gap refs at all -> violation
  - gap_ledger_ref only (no spec_fact_refs, no exception) -> violation
Positive controls:
  - gap_ledger_ref + spec_fact_refs -> no violation
  - gap_ledger_ref + exception_classification -> no violation
  - capability_ref + spec_fact_refs -> no violation
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from guard_001_checker import check_guard_001, check_guard_001_all  # noqa: E402


# ---------------------------------------------------------------------------
# Unit-level tests using guard_001_checker.check_guard_001_all directly.
# ---------------------------------------------------------------------------

def _guard001_violations(declaration: dict) -> list[str]:
    """Delegate to the real check_guard_001_all for accurate enforcement."""
    return check_guard_001_all(declaration.get("planned_work_items", []))


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

    def test_product_source_with_gap_ledger_ref_only_is_violation(self):
        """AND logic: gap_ledger_ref alone without spec authority -> violation (SAL-HEAL-A001)."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-AND-NEG-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Item with gap ref but no spec authority",
                "gap_ledger_ref": "GAP-FODS-0042",
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-AND-NEG-001" in violations, (
            f"gap_ledger_ref alone must be a violation under AND logic, got: {violations}"
        )

    def test_product_source_with_gap_ref_and_spec_fact_refs_passes(self):
        """POSITIVE CONTROL: gap_ledger_ref + spec_fact_refs -> no violation (AND logic)."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-POS-001",
                "item_type": "PRODUCT_SOURCE",
                "title": "Implement table:table canonical class",
                "gap_ledger_ref": "GAP-FODS-0042",
                "spec_fact_refs": ["FACT-FODS-001"],
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-POS-001" not in violations, (
            f"Expected no violation for item with gap_ledger_ref+spec_fact_refs, got: {violations}"
        )

    def test_product_source_with_gap_ref_and_exception_passes(self):
        """gap_ledger_ref + exception_classification -> no violation (AND logic)."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-EXC-001",
                "item_type": "PRODUCT_SOURCE",
                "gap_ledger_ref": "GAP-GNUMERIC-001",
                "exception_classification": "schema_authority_available",
                "evidence_paths": ["src/python/gnumeric/gnumeric_codec.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-EXC-001" not in violations

    def test_product_source_with_capability_ref_and_spec_fact_refs_passes(self):
        """capability_ref + spec_fact_refs satisfies AND logic."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-CAP-001",
                "item_type": "PRODUCT_SOURCE",
                "capability_ref": "CAP-FODS-table-count",
                "spec_fact_refs": ["FACT-FODS-004"],
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-CAP-001" not in violations

    def test_product_source_with_spec_fact_refs_only_is_violation(self):
        """spec_fact_refs alone without gap_ledger_ref -> violation (AND logic requires both)."""
        decl = {
            "planned_work_items": [{
                "item_id": "TC-G001-SPEC-ONLY-001",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["FACT-FODS-004"],
                "evidence_paths": ["src/python/fods/neutral_model.py"],
            }]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-SPEC-ONLY-001" in violations, (
            "spec_fact_refs alone without gap_ledger_ref/capability_ref must be a violation"
        )

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
                    # AND logic: needs BOTH gap_ledger_ref AND spec authority
                    "item_id": "TC-G001-MULTI-003",
                    "item_type": "PRODUCT_SOURCE",
                    "gap_ledger_ref": "GAP-FODS-0001",
                    "spec_fact_refs": ["FACT-FODS-001"],
                    "evidence_paths": ["src/python/fods/neutral_model.py"],
                },
            ]
        }
        violations = _guard001_violations(decl)
        assert "TC-G001-MULTI-001" in violations
        assert "TC-G001-MULTI-002" in violations
        assert "TC-G001-MULTI-003" not in violations  # has gap_ledger_ref + spec_fact_refs


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
