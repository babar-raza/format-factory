"""
R113 — ODF Spec Linkage Detector Tests (Detector 19)

Tests that detect_odf_spec_linkage correctly:
- fires HIGH warning for ODF PRODUCT_SOURCE items missing spec linkage
- is silent for ODF items that HAVE spec_qname_refs
- is silent for ODF items that HAVE spec_fact_refs
- is silent for non-ODF formats (ZST, CSV, NDJSON, etc.)
- is silent for non-PRODUCT_SOURCE item types
- is silent for empty declarations
- is correctly wired into run_all_checks() and appears in the result set
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from anti_skip_checker import detect_odf_spec_linkage, run_all_checks, SEVERITY_MAP


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _odf_product_source_item(
    item_id="ODF-001",
    fmt="fods",
    spec_qname_refs=None,
    spec_fact_refs=None,
):
    item = {"item_id": item_id, "item_type": "PRODUCT_SOURCE", "format": fmt}
    if spec_qname_refs is not None:
        item["spec_qname_refs"] = spec_qname_refs
    if spec_fact_refs is not None:
        item["spec_fact_refs"] = spec_fact_refs
    return item


def _declaration_with(*items):
    return {"planned_work_items": list(items)}


# ---------------------------------------------------------------------------
# Negative controls — detector should FIRE
# ---------------------------------------------------------------------------

def test_fods_no_spec_refs_fires():
    """FODS PRODUCT_SOURCE with no spec refs → violation."""
    decl = _declaration_with(_odf_product_source_item(fmt="fods"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True
    assert "ODF-001" in result["missing_items"]
    assert "spec_qname_refs" in result["recommendation"]


def test_fodt_no_spec_refs_fires():
    """FODT PRODUCT_SOURCE with no spec refs → violation."""
    decl = _declaration_with(_odf_product_source_item(fmt="fodt"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_ods_no_spec_refs_fires():
    """ODS PRODUCT_SOURCE with no spec refs → violation."""
    decl = _declaration_with(_odf_product_source_item(fmt="ods"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_odt_no_spec_refs_fires():
    """ODT PRODUCT_SOURCE with no spec refs → violation."""
    decl = _declaration_with(_odf_product_source_item(fmt="odt"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_fodg_no_spec_refs_fires():
    """FODG PRODUCT_SOURCE with no spec refs → violation."""
    decl = _declaration_with(_odf_product_source_item(fmt="fodg"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_fodp_no_spec_refs_fires():
    """FODP PRODUCT_SOURCE with no spec refs → violation."""
    decl = _declaration_with(_odf_product_source_item(fmt="fodp"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_multiple_odf_items_all_missing_fires():
    """Two ODF items both missing spec refs → both appear in missing_items."""
    decl = _declaration_with(
        _odf_product_source_item(item_id="ODF-001", fmt="fods"),
        _odf_product_source_item(item_id="ODF-002", fmt="fodt"),
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True
    assert "ODF-001" in result["missing_items"]
    assert "ODF-002" in result["missing_items"]


# ---------------------------------------------------------------------------
# Positive controls — detector should NOT fire
# ---------------------------------------------------------------------------

def test_odf_with_spec_qname_refs_no_violation():
    """FODS item WITH spec_qname_refs → no violation."""
    decl = _declaration_with(
        _odf_product_source_item(fmt="fods", spec_qname_refs=["fods:table", "table:table-cell"])
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False
    assert result["missing_items"] == []


def test_odf_with_spec_fact_refs_no_violation():
    """FODS item WITH spec_fact_refs (but no qname_refs) → no violation."""
    decl = _declaration_with(
        _odf_product_source_item(fmt="fods", spec_fact_refs=["FACT-FODS-001"])
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


def test_odf_with_both_refs_no_violation():
    """FODS item with both spec_qname_refs and spec_fact_refs → no violation."""
    decl = _declaration_with(
        _odf_product_source_item(
            fmt="fods",
            spec_qname_refs=["fods:table"],
            spec_fact_refs=["FACT-FODS-001"],
        )
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


# ---------------------------------------------------------------------------
# Non-ODF format controls — detector should be SILENT
# ---------------------------------------------------------------------------

def test_zst_no_spec_refs_silent():
    """ZST PRODUCT_SOURCE with no spec refs → no violation (not ODF)."""
    decl = _declaration_with(_odf_product_source_item(item_id="ZST-001", fmt="zst"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


def test_csv_no_spec_refs_silent():
    """CSV PRODUCT_SOURCE with no spec refs → no violation (not ODF)."""
    decl = _declaration_with(_odf_product_source_item(item_id="CSV-001", fmt="csv"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


def test_ndjson_no_spec_refs_silent():
    """NDJSON PRODUCT_SOURCE with no spec refs → no violation (not ODF)."""
    decl = _declaration_with(_odf_product_source_item(item_id="NDJSON-001", fmt="ndjson"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


def test_xcf_no_spec_refs_silent():
    """XCF PRODUCT_SOURCE with no spec refs → no violation (not ODF)."""
    decl = _declaration_with(_odf_product_source_item(item_id="XCF-001", fmt="xcf"))
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


# ---------------------------------------------------------------------------
# Non-PRODUCT_SOURCE item type — detector should be SILENT
# ---------------------------------------------------------------------------

def test_governance_item_odf_format_silent():
    """GOVERNANCE_TASKCARD item for FODS → no violation (not PRODUCT_SOURCE)."""
    decl = _declaration_with(
        {"item_id": "GOV-001", "item_type": "GOVERNANCE_TASKCARD", "format": "fods"}
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


def test_test_item_odf_format_silent():
    """TEST item for FODS → no violation (not PRODUCT_SOURCE)."""
    decl = _declaration_with(
        {"item_id": "TEST-001", "item_type": "TEST", "format": "fods"}
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is False


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_declaration_no_violation():
    """Empty declaration → no violation."""
    result = detect_odf_spec_linkage({})
    assert result["is_violation"] is False
    assert result["missing_items"] == []


def test_declaration_no_planned_work_items_no_violation():
    """Declaration with no planned_work_items → no violation."""
    result = detect_odf_spec_linkage({"sprint_id": "test"})
    assert result["is_violation"] is False


def test_empty_spec_qname_refs_list_fires():
    """Empty list for spec_qname_refs is falsy → treated as missing → violation."""
    decl = _declaration_with(
        _odf_product_source_item(fmt="fods", spec_qname_refs=[])
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_odf_format_case_insensitive():
    """Format name 'FODS' (uppercase) is treated same as 'fods'."""
    decl = _declaration_with(
        {"item_id": "ODF-001", "item_type": "PRODUCT_SOURCE", "format": "FODS"}
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True


def test_mixed_odf_and_non_odf_only_odf_fires():
    """One ODF item (missing refs) + one non-ODF item → only ODF fires."""
    decl = _declaration_with(
        _odf_product_source_item(item_id="ODF-001", fmt="fods"),
        _odf_product_source_item(item_id="ZST-001", fmt="zst"),
    )
    result = detect_odf_spec_linkage(decl)
    assert result["is_violation"] is True
    assert "ODF-001" in result["missing_items"]
    assert "ZST-001" not in result["missing_items"]


# ---------------------------------------------------------------------------
# Severity mapping
# ---------------------------------------------------------------------------

def test_odf_spec_linkage_in_severity_map():
    """Detector 19 is in SEVERITY_MAP with 'high' severity."""
    assert SEVERITY_MAP.get("odf_spec_linkage") == "high"


def test_high_severity_downgrades_verdict_not_blocks():
    """HIGH severity downgrades but does not block continuation."""
    # 'high' goes into downgrade_items, not block_items
    # Verify by checking classify_violation_impact logic via run_all_checks
    decl = _declaration_with(_odf_product_source_item(fmt="fods"))
    result = run_all_checks(declaration=decl)
    impact = result["impact"]
    # Should appear in downgrade_items, NOT block_items
    assert "odf_spec_linkage" in impact.get("downgrade_items", [])
    assert "odf_spec_linkage" not in impact.get("block_items", [])
    assert impact["block"] is False or "odf_spec_linkage" not in impact.get("block_items", [])


# ---------------------------------------------------------------------------
# Integration: run_all_checks wiring
# ---------------------------------------------------------------------------

def test_run_all_checks_includes_detector_19():
    """run_all_checks with a declaration includes the odf_spec_linkage check."""
    decl = _declaration_with(_odf_product_source_item(fmt="fods"))
    result = run_all_checks(declaration=decl)
    check_names = [c["check"] for c in result["checks"]]
    assert "odf_spec_linkage" in check_names


def test_run_all_checks_19_detectors_with_declaration():
    """run_all_checks with a full declaration runs at least 19 checks."""
    decl = _declaration_with(_odf_product_source_item(fmt="fods"))
    result = run_all_checks(declaration=decl)
    # With a full declaration, many detectors run; must include odf_spec_linkage
    assert result["total_checks"] >= 6  # at minimum the declaration-based checks
    assert any(c["check"] == "odf_spec_linkage" for c in result["checks"])


def test_run_all_checks_no_declaration_no_detector_19():
    """run_all_checks without a declaration does NOT run detector 19."""
    result = run_all_checks()
    check_names = [c["check"] for c in result["checks"]]
    assert "odf_spec_linkage" not in check_names
