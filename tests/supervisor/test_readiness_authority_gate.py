"""
test_readiness_authority_gate.py

Tests for READINESS and RELEASE_GATE authority enforcement via V13 governance validator.

SAL-VERIFICATION-HARDENING-001 (Lane D) — 2026-06-11
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import validate_spec_fact_refs_wired


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(item_type: str, item_id: str = "TEST-001", spec_fact_refs=None,
          exception_classification: str = "") -> dict:
    return {
        "item_id": item_id,
        "title": f"Test {item_type} item",
        "item_type": item_type,
        "status": "completed",
        "spec_fact_refs": spec_fact_refs or [],
        "exception_classification": exception_classification,
        "execution_method": "LOCAL_GOVERNED_DIRECT_EXECUTION",
    }


def _decl(items: list) -> dict:
    return {
        "sprint_id": "TEST-RDNS",
        "run_id": "test-rdns-001",
        "planned_work_items": items,
    }


# ---------------------------------------------------------------------------
# Test 1: READINESS without authority is blocked
# ---------------------------------------------------------------------------

class TestReadinessWithoutAuthorityIsBlocked:
    def test_readiness_item_without_fact_refs_blocked(self):
        """READINESS item with no spec_fact_refs and no exception must FAIL + block."""
        item = _item("READINESS", item_id="RDNS-001", spec_fact_refs=[],
                     exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_readiness_with_debt_exception_blocked(self):
        """READINESS with no_public_spec_available (debt-only) must FAIL + block."""
        item = _item("READINESS", item_id="RDNS-002", spec_fact_refs=[],
                     exception_classification="no_public_spec_available")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_readiness_with_schema_authority_debt_blocked(self):
        """READINESS with schema_authority_available (debt-only) must FAIL + block."""
        item = _item("READINESS", item_id="RDNS-003", spec_fact_refs=[],
                     exception_classification="schema_authority_available")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_readiness_with_fallback_authority_approved_not_blocked(self):
        """READINESS with fallback_authority_approved + rationale must NOT block."""
        item = _item("READINESS", item_id="RDNS-004", spec_fact_refs=[],
                     exception_classification="fallback_authority_approved")
        item["exception_rationale"] = "Approved by governance reviewer — see SAL-I-003"
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False

    def test_readiness_with_valid_fact_refs_not_blocked(self):
        """READINESS with valid FACT-* refs must NOT block."""
        item = _item("READINESS", item_id="RDNS-005",
                     spec_fact_refs=["FACT-ZST-001"],
                     exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False


# ---------------------------------------------------------------------------
# Test 2: RELEASE_GATE without authority is blocked
# ---------------------------------------------------------------------------

class TestReleaseGateWithoutAuthorityIsBlocked:
    def test_release_gate_without_fact_refs_blocked(self):
        """RELEASE_GATE without fact refs must FAIL + block."""
        item = _item("RELEASE_GATE", item_id="RG-001", spec_fact_refs=[],
                     exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_release_gate_with_legacy_backfill_blocked(self):
        """RELEASE_GATE with legacy_backfill exception must still FAIL (cannot release with debt)."""
        item = _item("RELEASE_GATE", item_id="RG-002", spec_fact_refs=[],
                     exception_classification="legacy_backfill")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Test 3: run_all_governance_validators blocks for READINESS
# ---------------------------------------------------------------------------

class TestRunAllValidatorsBlocksReadiness:
    def test_v13_blocks_for_readiness_without_authority(self):
        """V13 (spec_fact_refs_wired) must block when READINESS item lacks authority."""
        item = _item("READINESS", item_id="RDNS-RUN-ALL", spec_fact_refs=[],
                     exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
