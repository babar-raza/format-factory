"""
test_integration_end_to_end.py

Lane G: End-to-end integration pilots proving the SAL enforcement path works.

Five pilots:
  P1: ZST positive — FACT-ZST-* ref present → governance ALLOWS
  P2: FODS positive — FACT-FODS-* ref present → governance ALLOWS
  P3: ABW negative — no exception → governance BLOCKS
  P4: DIF regression — R2 tests still pass (tested elsewhere; governance path checked here)
  P5: Netpbm positive — FACT-PBM-* ref present → governance ALLOWS

SAL-VERIFICATION-HARDENING-001 (Lane G) — 2026-06-11
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

def _product_source_item(item_id: str, format_id: str, spec_fact_refs=None,
                          exception_classification: str = "") -> dict:
    return {
        "item_id": item_id,
        "title": f"Product source for {format_id}",
        "item_type": "PRODUCT_SOURCE",
        "status": "completed",
        "format_id": format_id,
        "spec_fact_refs": spec_fact_refs or [],
        "exception_classification": exception_classification,
        "execution_method": "LOCAL_GOVERNED_DIRECT_EXECUTION",
        "idempotency_key": "a" * 64,
        "claim_classification": "GOVERNED_AND_REPLAYABLE",
    }


def _decl(items: list) -> dict:
    return {
        "sprint_id": "TEST-E2E-PILOT",
        "run_id": "test-e2e-pilot-001",
        "planned_work_items": items,
    }


# ---------------------------------------------------------------------------
# Pilot P1: ZST positive
# ---------------------------------------------------------------------------

class TestPilotP1ZSTPositive:
    """ZST PRODUCT_SOURCE item with FACT-ZST-* ref must pass governance."""

    def test_zst_with_fact_ref_passes_governance(self):
        item = _product_source_item("ZST-P1-001", "zst",
                                     spec_fact_refs=["FACT-ZST-001"])
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False, (
            f"ZST with FACT-ZST-001 must pass. errors: {result.get('items', [])}"
        )

    def test_zst_with_fact_ref_passes_run_all(self):
        item = _product_source_item("ZST-P1-002", "zst",
                                     spec_fact_refs=["FACT-ZST-001", "FACT-ZST-002"])
        result = run_all_governance_validators(_decl([item]))
        sfr = next(v for v in result["validators"]
                   if v["validator"] == "spec_fact_refs_validator")
        assert sfr["result"] != "FAIL", f"V13 must not FAIL for ZST with refs: {sfr}"
        # Other validators may fail (no idempotency_key details, etc.) — focus on V13
        assert sfr["blocks_sprint"] is False


# ---------------------------------------------------------------------------
# Pilot P2: FODS positive
# ---------------------------------------------------------------------------

class TestPilotP2FODSPositive:
    """FODS PRODUCT_SOURCE item with FACT-FODS-* ref must pass governance."""

    def test_fods_with_fact_ref_passes_governance(self):
        item = _product_source_item("FODS-P2-001", "fods",
                                     spec_fact_refs=["FACT-FODS-001"])
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False, (
            f"FODS with FACT-FODS-001 must pass. errors: {result.get('items', [])}"
        )


# ---------------------------------------------------------------------------
# Pilot P3: ABW negative (no exception)
# ---------------------------------------------------------------------------

class TestPilotP3ABWNegative:
    """ABW PRODUCT_SOURCE without exception must be BLOCKED by V13."""

    def test_abw_without_exception_blocked_by_governance(self):
        item = _product_source_item("ABW-P3-001", "abw",
                                     spec_fact_refs=[],
                                     exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_abw_with_no_public_spec_exception_passes(self):
        """ABW with no_public_spec_available exception must NOT block."""
        item = _product_source_item("ABW-P3-002", "abw",
                                     spec_fact_refs=[],
                                     exception_classification="no_public_spec_available")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False, (
            f"ABW with no_public_spec_available must pass. errors: {result.get('items', [])}"
        )

    def test_abw_blocked_confirmed_in_run_all(self):
        """run_all_governance_validators must set blocks_sprint=True for ABW without exception."""
        item = _product_source_item("ABW-P3-003", "abw",
                                     spec_fact_refs=[],
                                     exception_classification="")
        result = run_all_governance_validators(_decl([item]))
        sfr = next(v for v in result["validators"]
                   if v["validator"] == "spec_fact_refs_validator")
        assert sfr["result"] == "FAIL"
        assert sfr["blocks_sprint"] is True
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Pilot P4: DIF regression
# ---------------------------------------------------------------------------

class TestPilotP4DIFRegression:
    """DIF format: no_public_spec_available exception must allow expansion."""

    def test_dif_with_no_public_spec_passes(self):
        item = _product_source_item("DIF-P4-001", "dif",
                                     spec_fact_refs=[],
                                     exception_classification="no_public_spec_available")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False

    def test_dif_without_exception_blocked(self):
        """DIF without exception_classification must be blocked (no public spec)."""
        item = _product_source_item("DIF-P4-002", "dif",
                                     spec_fact_refs=[],
                                     exception_classification="")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# Pilot P5: Netpbm (PBM) positive
# ---------------------------------------------------------------------------

class TestPilotP5NetpbmPositive:
    """Netpbm (PBM) PRODUCT_SOURCE with FACT-PBM-* ref must pass governance."""

    def test_pbm_with_fact_ref_passes_governance(self):
        item = _product_source_item("PBM-P5-001", "pbm",
                                     spec_fact_refs=["FACT-PBM-001"])
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False

    def test_pgm_with_fact_ref_passes_governance(self):
        item = _product_source_item("PGM-P5-001", "pgm",
                                     spec_fact_refs=["FACT-PGM-001"])
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False

    def test_ppm_with_fact_ref_passes_governance(self):
        item = _product_source_item("PPM-P5-001", "ppm",
                                     spec_fact_refs=["FACT-PPM-001"])
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["blocks_sprint"] is False
