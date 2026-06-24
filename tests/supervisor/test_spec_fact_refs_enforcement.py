"""
test_spec_fact_refs_enforcement.py
Sprint: SPEC-AUTHORITY-LAYER-STOP-THE-BLEEDING-REPAIR-AND-ENFORCEMENT-001
Added: 2026-06-07

Tests for spec_fact_refs BLOCKING enforcement gate.

10 negative/positive test cases proving:
1. PRODUCT_SOURCE without spec_fact_refs and without exception is rejected.
2. PRODUCT_SOURCE with valid spec_fact_refs is accepted.
3. PRODUCT_SOURCE with legacy_backfill is accepted only as debt and cannot claim readiness.
4. PRODUCT_SOURCE with investigation_only but product source changes is accepted (files not checked here).
5. PRODUCT_SOURCE with invalid fact ID is rejected.
6. PRODUCT_SOURCE with schema_authority_available requires no additional reference (authority type is self-declaring).
7. AI-only authority (no valid exception) is rejected.
8. TEST item without spec refs or valid exception is rejected.
9. RELEASE_GATE without spec refs or valid exception is rejected.
10. Existing investigation-only items remain allowed.
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))

from validate_spec_fact_refs import (
    check_item,
    validate_declaration_spec_fact_refs,
    BLOCKING_ITEM_TYPES,
    VALID_EXCEPTION_CLASSIFICATIONS,
)


class TestBlockingEnforcementNegative:
    """Negative tests: these scenarios MUST be rejected."""

    def test_product_source_no_refs_no_exception_is_rejected(self):
        """PRODUCT_SOURCE with empty spec_fact_refs and no exception_classification is BLOCKED."""
        item = {
            "item_id": "WI-TEST-NEG-001",
            "item_type": "PRODUCT_SOURCE",
            "title": "Some product source work",
            "status": "completed",
        }
        result = check_item(item)
        assert not result["compliant"], "Should be non-compliant"
        assert result["grade_impact"] == "reject", f"Expected reject, got {result['grade_impact']}"
        assert "BLOCKING" in result["violation"], "Violation should mention BLOCKING gate"

    def test_product_source_empty_refs_no_exception_is_rejected(self):
        """PRODUCT_SOURCE with explicit empty spec_fact_refs list and no exception is BLOCKED."""
        item = {
            "item_id": "WI-TEST-NEG-002",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
            "status": "completed",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"

    def test_product_source_invalid_fact_id_format_is_rejected(self):
        """spec_fact_refs with malformed fact IDs are rejected (must match FACT-<FORMAT>-<N>)."""
        item = {
            "item_id": "WI-TEST-NEG-003",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": ["NOT-A-FACT", "also-wrong"],
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "Invalid spec_fact_ref format" in result["violation"]

    def test_invalid_exception_classification_is_rejected(self):
        """An unrecognized exception_classification is always rejected."""
        item = {
            "item_id": "WI-TEST-NEG-004",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
            "exception_classification": "ai_only_authority",  # not a valid classification
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "not a valid classification" in result["violation"]

    def test_test_item_no_refs_no_exception_is_rejected(self):
        """TEST work items are in blocking_item_types. No refs + no exception = rejected."""
        item = {
            "item_id": "WI-TEST-NEG-005",
            "item_type": "TEST",
            "title": "Some test work",
            "status": "completed",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"

    def test_release_gate_no_refs_no_exception_is_rejected(self):
        """RELEASE_GATE items require spec_fact_refs or a valid exception."""
        item = {
            "item_id": "WI-TEST-NEG-006",
            "item_type": "RELEASE_GATE",
            "status": "completed",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"

    def test_legacy_backfill_cannot_claim_readiness(self):
        """READINESS items with legacy_backfill exception are rejected — debt cannot gate readiness."""
        item = {
            "item_id": "WI-TEST-NEG-007",
            "item_type": "READINESS",
            "spec_fact_refs": [],
            "exception_classification": "legacy_backfill",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "debt" in result["violation"].lower() or "readiness" in result["violation"].lower()

    def test_no_public_spec_available_cannot_claim_release_gate(self):
        """RELEASE_GATE items with no_public_spec_available are rejected (debt-only exception)."""
        item = {
            "item_id": "WI-TEST-NEG-008",
            "item_type": "RELEASE_GATE",
            "spec_fact_refs": [],
            "exception_classification": "no_public_spec_available",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"

    def test_fallback_authority_without_rationale_is_rejected(self):
        """fallback_authority_approved without exception_rationale is rejected."""
        item = {
            "item_id": "WI-TEST-NEG-009",
            "item_type": "TEST",
            "spec_fact_refs": [],
            "exception_classification": "fallback_authority_approved",
            # no exception_rationale
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "rationale" in result["violation"].lower()

    def test_declaration_with_blocking_violation_is_non_compliant(self):
        """Full declaration validation catches blocking violations across multiple items."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-001",
                    "item_type": "PRODUCT_SOURCE",
                    "title": "Product work without authority",
                    "status": "completed",
                    # No spec_fact_refs, no exception_classification
                },
                {
                    "item_id": "WI-002",
                    "item_type": "INVESTIGATION",  # Non-blocking type
                    "title": "Investigation",
                    "status": "completed",
                },
            ]
        }
        result = validate_declaration_spec_fact_refs(decl)
        assert not result["compliant"]
        assert len(result["errors"]) == 1
        assert "WI-001" in result["errors"][0]


class TestBlockingEnforcementPositive:
    """Positive tests: these scenarios MUST be accepted."""

    def test_product_source_with_valid_refs_is_accepted(self):
        """PRODUCT_SOURCE with properly formatted spec_fact_refs is accepted."""
        item = {
            "item_id": "WI-TEST-POS-001",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": ["FACT-FODS-001", "FACT-FODS-003"],
        }
        result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "none"

    def test_product_source_with_investigation_only_is_accepted(self):
        """PRODUCT_SOURCE with investigation_only exception is accepted (no debt)."""
        item = {
            "item_id": "WI-TEST-POS-002",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
            "exception_classification": "investigation_only",
        }
        result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "none"

    def test_product_source_with_legacy_backfill_is_accepted_as_debt(self):
        """PRODUCT_SOURCE with legacy_backfill is accepted but marked as authority debt."""
        item = {
            "item_id": "WI-TEST-POS-003",
            "item_type": "PRODUCT_SOURCE",
            "spec_fact_refs": [],
            "exception_classification": "legacy_backfill",
        }
        result = check_item(item)
        assert result["compliant"], f"Should be compliant: {result}"
        assert result["grade_impact"] == "debt"

    def test_non_blocking_type_always_passes(self):
        """Non-blocking item_types (DOCUMENTATION, INVESTIGATION, etc.) always pass."""
        for item_type in ["DOCUMENTATION", "INVESTIGATION", "GOVERNANCE", "AUDIT", "INFRA"]:
            item = {"item_id": f"WI-{item_type}", "item_type": item_type}
            result = check_item(item)
            assert result["compliant"], f"{item_type} should be compliant: {result}"
            assert not result["blocking_type"]

    def test_schema_authority_available_on_readiness_is_rejected(self):
        """schema_authority_available is debt-only — cannot claim READINESS (DEBT-005 repair)."""
        item = {
            "item_id": "WI-TEST-POS-005",
            "item_type": "READINESS",
            "spec_fact_refs": [],
            "exception_classification": "schema_authority_available",
        }
        result = check_item(item)
        assert not result["compliant"]
        assert result["grade_impact"] == "reject"
        assert "debt/grace classification" in result["violation"]

    def test_fallback_authority_approved_with_rationale_is_accepted(self):
        """fallback_authority_approved with exception_rationale is accepted."""
        item = {
            "item_id": "WI-TEST-POS-006",
            "item_type": "TEST",
            "spec_fact_refs": [],
            "exception_classification": "fallback_authority_approved",
            "exception_rationale": "Approved by Babar Raza on 2026-06-07 — format is internal-only.",
        }
        result = check_item(item)
        assert result["compliant"]

    def test_requirement_with_valid_refs_is_accepted(self):
        """REQUIREMENT item with valid spec_fact_refs is accepted."""
        item = {
            "item_id": "WI-TEST-POS-007",
            "item_type": "REQUIREMENT",
            "spec_fact_refs": ["FACT-FODS-003"],
        }
        result = check_item(item)
        assert result["compliant"]
        assert result["grade_impact"] == "none"

    def test_declaration_all_compliant_passes(self):
        """Declaration where all blocking items have valid authority passes."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-001",
                    "item_type": "PRODUCT_SOURCE",
                    "spec_fact_refs": ["FACT-FODS-001"],
                },
                {
                    "item_id": "WI-002",
                    "item_type": "REQUIREMENT",
                    "exception_classification": "investigation_only",
                },
                {
                    "item_id": "WI-003",
                    "item_type": "INVESTIGATION",
                },
            ]
        }
        result = validate_declaration_spec_fact_refs(decl)
        assert result["compliant"]
        assert len(result["errors"]) == 0


class TestBlockingItemTypes:
    """Verify the blocking types list is complete and stable."""

    def test_all_required_blocking_types_present(self):
        """All five mandated blocking types must be in BLOCKING_ITEM_TYPES."""
        required = {"PRODUCT_SOURCE", "TEST", "REQUIREMENT", "READINESS", "RELEASE_GATE"}
        assert required.issubset(BLOCKING_ITEM_TYPES)

    def test_valid_exception_classifications_complete(self):
        """All six valid exception classifications must be present."""
        required = {
            "investigation_only",
            "sample_only_non_product",
            "legacy_backfill",
            "fallback_authority_approved",
            "no_public_spec_available",
            "schema_authority_available",
        }
        assert required.issubset(VALID_EXCEPTION_CLASSIFICATIONS)
