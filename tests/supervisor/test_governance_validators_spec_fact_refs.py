"""
test_governance_validators_spec_fact_refs.py

Tests for V13: spec_fact_refs validator integration in run_all_governance_validators.

Added: SAL-VERIFICATION-HARDENING-001 (Lane B) — 2026-06-11
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import run_all_governance_validators, validate_spec_fact_refs_wired


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _prod_item(item_id: str, spec_fact_refs=None, exception_classification="",
               item_type="PRODUCT_SOURCE") -> dict:
    return {
        "item_id": item_id,
        "title": f"Test item {item_id}",
        "item_type": item_type,
        "status": "completed",
        "spec_fact_refs": spec_fact_refs or [],
        "exception_classification": exception_classification,
        "execution_method": "LOCAL_GOVERNED_DIRECT_EXECUTION",
    }


def _decl(items: list) -> dict:
    return {
        "sprint_id": "TEST-SFR",
        "run_id": "test-sfr-001",
        "planned_work_items": items,
    }


# ---------------------------------------------------------------------------
# Test 1: V13 is included in run_all_governance_validators
# ---------------------------------------------------------------------------

class TestGovernanceValidatorsIncludesSpecFactRefs:
    def test_governance_validators_includes_spec_fact_refs(self):
        """V13 spec_fact_refs validator must appear in run_all results."""
        result = run_all_governance_validators(_decl([]))
        names = [v["validator"] for v in result["validators"]]
        assert "spec_fact_refs_validator" in names

    def test_governance_validators_count_is_13(self):
        """Total validator count must be 13 (12 original + V13)."""
        result = run_all_governance_validators(_decl([]))
        assert len(result["validators"]) == 13


# ---------------------------------------------------------------------------
# Test 2: PRODUCT_SOURCE without FACT-* ref and no exception blocks
# ---------------------------------------------------------------------------

class TestProductSourceWithoutFactRefBlocks:
    def test_product_source_without_fact_ref_blocks(self):
        """PRODUCT_SOURCE with no spec_fact_refs and no exception must FAIL + block."""
        item = _prod_item("PS-NO-REF", spec_fact_refs=[], exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_product_source_without_fact_ref_blocks_in_run_all(self):
        """run_all_governance_validators must block when V13 fails."""
        item = _prod_item("PS-NO-REF-2", spec_fact_refs=[], exception_classification="")
        result = run_all_governance_validators(_decl([item]))
        sfr = next(v for v in result["validators"] if v["validator"] == "spec_fact_refs_validator")
        assert sfr["result"] == "FAIL"
        assert sfr["blocks_sprint"] is True
        # The overall blocks_sprint must be True because V13 fails
        assert result["blocks_sprint"] is True

    def test_readiness_without_fact_ref_blocks(self):
        """READINESS without spec_fact_refs and no exception must FAIL + block."""
        item = _prod_item("RDNS-NO-REF", spec_fact_refs=[], exception_classification="",
                          item_type="READINESS")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_release_gate_without_fact_ref_blocks(self):
        """RELEASE_GATE without spec_fact_refs must FAIL + block."""
        item = _prod_item("RG-NO-REF", spec_fact_refs=[], exception_classification="",
                          item_type="RELEASE_GATE")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Test 3: PRODUCT_SOURCE with valid FACT-* ref passes or does not block
# ---------------------------------------------------------------------------

class TestProductSourceWithValidFactRefPasses:
    def test_product_source_with_valid_fact_ref_passes(self):
        """PRODUCT_SOURCE with valid FACT-ZST-001 ref must PASS (if registry absent, graceful)."""
        # Reset fact registry cache for clean test
        from validate_spec_fact_refs import reset_fact_registry_cache
        reset_fact_registry_cache()
        item = _prod_item("PS-WITH-REF", spec_fact_refs=["FACT-ZST-001"])
        result = validate_spec_fact_refs_wired(_decl([item]))
        # If fact registry exists and FACT-ZST-001 is present → PASS
        # If fact registry empty (graceful degradation) → PASS (no registry to check against)
        # Either way, must NOT block
        assert result["blocks_sprint"] is False


# ---------------------------------------------------------------------------
# Test 4: PRODUCT_SOURCE with no_public_spec_available warns but does not block
# ---------------------------------------------------------------------------

class TestProductSourceWithNoPubSpecExceptionWarnsNotBlocks:
    def test_product_source_with_no_public_spec_exception_warns_not_blocks(self):
        """PRODUCT_SOURCE with no_public_spec_available must WARN, not FAIL."""
        item = _prod_item("PS-NO-SPEC", spec_fact_refs=[],
                          exception_classification="no_public_spec_available")
        result = validate_spec_fact_refs_wired(_decl([item]))
        # Should be WARN (debt) or PASS (no violation) — must NOT be FAIL
        assert result["result"] in ("WARN", "PASS")
        assert result["blocks_sprint"] is False

    def test_legacy_backfill_warns_not_blocks(self):
        """legacy_backfill exception must WARN but not hard-block."""
        item = _prod_item("PS-LEGACY", spec_fact_refs=[],
                          exception_classification="legacy_backfill")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] in ("WARN", "PASS")
        assert result["blocks_sprint"] is False


# ---------------------------------------------------------------------------
# Test 5: READINESS on debt-only exception blocks
# ---------------------------------------------------------------------------

class TestReadinessWithoutAuthorityBlocksOrDowngrades:
    def test_readiness_with_no_public_spec_blocks(self):
        """READINESS with debt-only exception (no_public_spec_available) must FAIL."""
        item = _prod_item("RDNS-DEBT", spec_fact_refs=[],
                          exception_classification="no_public_spec_available",
                          item_type="READINESS")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_readiness_with_schema_authority_blocks(self):
        """READINESS with schema_authority_available (debt-only) must FAIL."""
        item = _prod_item("RDNS-SCHEMA", spec_fact_refs=[],
                          exception_classification="schema_authority_available",
                          item_type="READINESS")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Test 6: RELEASE_GATE without authority blocks
# ---------------------------------------------------------------------------

class TestReleaseGateWithoutAuthorityBlocks:
    def test_release_gate_without_fact_refs_blocks(self):
        """RELEASE_GATE without fact refs and no exception must FAIL + block."""
        item = _prod_item("RG-NO-AUTH", spec_fact_refs=[], exception_classification="",
                          item_type="RELEASE_GATE")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_release_gate_with_debt_exception_blocks(self):
        """RELEASE_GATE with legacy_backfill exception must FAIL (debt cannot release)."""
        item = _prod_item("RG-LEGACY", spec_fact_refs=[],
                          exception_classification="legacy_backfill",
                          item_type="RELEASE_GATE")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Test 7: AI-only authority claim rejected
# ---------------------------------------------------------------------------

class TestAiOnlyAuthorityClaimRejected:
    def test_invalid_exception_classification_rejected(self):
        """Exception classification 'ai_generated' is invalid — must FAIL."""
        item = _prod_item("PS-AI-ONLY", spec_fact_refs=[],
                          exception_classification="ai_generated_authority")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_raw_ai_summary_classification_rejected(self):
        """Exception classification 'raw_ai_summary' is invalid — must FAIL."""
        item = _prod_item("PS-RAW-AI", spec_fact_refs=[],
                          exception_classification="raw_ai_summary_only")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Test 8: GOVERNANCE_DOC items are not affected (non-blocking types)
# ---------------------------------------------------------------------------

class TestNonBlockingItemTypesNotAffected:
    def test_governance_doc_passes_without_spec_fact_refs(self):
        """GOVERNANCE_DOC items are never subject to spec_fact_refs enforcement."""
        item = {
            "item_id": "GOV-DOC-001",
            "title": "Governance doc",
            "item_type": "GOVERNANCE_DOC",
            "status": "completed",
            "spec_fact_refs": [],
        }
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_empty_declaration_passes(self):
        """Empty planned_work_items passes spec_fact_refs enforcement."""
        result = validate_spec_fact_refs_wired(_decl([]))
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
