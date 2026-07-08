"""TC-VALIDATOR-REMAINING-001: Integration tests for the 6 remaining spec-parity validators.

Covers V13, V14, V37, V47, V51, V53 — the validators not tested in
test_spec_parity_validators_product_source.py (which tested V13a/V23/V24).

These tests verify enforcement boundaries: FAIL/WARN on non-compliant declarations,
PASS on compliant ones.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "specification-authority-layer"))


def _decl(items: list[dict]) -> dict:
    return {"planned_work_items": items, "changed_files": []}


def _product_source(item_id: str = "TC-T-001", **kwargs) -> dict:
    return {"item_id": item_id, "item_type": "PRODUCT_SOURCE", "title": "test", **kwargs}


def _release_gate(item_id: str = "TC-G-001", **kwargs) -> dict:
    return {"item_id": item_id, "item_type": "RELEASE_GATE", "title": "test", **kwargs}


# ---------------------------------------------------------------------------
# V13 — validate_spec_fact_refs_wired
# ---------------------------------------------------------------------------

class TestValidateSpecFactRefsWired:
    """V13: PRODUCT_SOURCE/RELEASE_GATE without spec_fact_refs must be BLOCKED."""

    def test_empty_declaration_passes(self) -> None:
        from governance_validators import validate_spec_fact_refs_wired
        result = validate_spec_fact_refs_wired(_decl([]))
        assert result["result"] == "PASS", f"Expected PASS, got {result['result']}: {result}"

    def test_product_source_without_spec_fact_refs_is_blocked(self) -> None:
        """PRODUCT_SOURCE item with no spec_fact_refs and no exception_classification → FAIL."""
        from governance_validators import validate_spec_fact_refs_wired
        item = _product_source()
        result = validate_spec_fact_refs_wired(_decl([item]))
        # Must be FAIL and must block sprint
        assert result["result"] == "FAIL", (
            f"Expected FAIL for PRODUCT_SOURCE without spec_fact_refs; got {result['result']}. "
            f"Full result: {result}"
        )
        assert result.get("blocks_sprint") is True, (
            f"blocks_sprint must be True for V13 failure; got {result.get('blocks_sprint')}"
        )

    def test_product_source_with_exception_classification_passes(self) -> None:
        """PRODUCT_SOURCE with a valid exception_classification is EXEMPT."""
        from governance_validators import validate_spec_fact_refs_wired
        item = _product_source(exception_classification="investigation_only")
        result = validate_spec_fact_refs_wired(_decl([item]))
        assert result["result"] == "PASS", (
            f"PRODUCT_SOURCE with exception_classification should PASS; got {result['result']}"
        )


# ---------------------------------------------------------------------------
# V14 — validate_spec_fact_count
# ---------------------------------------------------------------------------

class TestValidateSpecFactCount:
    """V14: Advisory spec-fact count check — always PASS in current implementation."""

    def test_empty_declaration_passes(self) -> None:
        from governance_validators import validate_spec_fact_count
        result = validate_spec_fact_count(_decl([]))
        assert result["result"] == "PASS"
        assert result.get("blocks_sprint") is False, "V14 must be advisory (blocks_sprint=False)"

    def test_product_source_with_refs_passes(self) -> None:
        from governance_validators import validate_spec_fact_count
        item = _product_source(spec_fact_refs=["FACT-FODS-001", "FACT-FODS-002"])
        result = validate_spec_fact_count(_decl([item]))
        assert result["result"] == "PASS"
        assert result.get("blocks_sprint") is False, "V14 must be advisory (blocks_sprint=False)"


# ---------------------------------------------------------------------------
# V37 — validate_spec_fact_authority_chain
# ---------------------------------------------------------------------------

class TestValidateSpecFactAuthorityChain:
    """V37: ODF PRODUCT_SOURCE items without spec_fact_refs → WARN."""

    def test_no_odf_items_passes(self) -> None:
        from governance_validators import validate_spec_fact_authority_chain
        # Non-ODF format_id should not trigger V37
        item = _product_source(format_id="csv")
        result = validate_spec_fact_authority_chain(_decl([item]))
        assert result["result"] == "PASS", (
            f"Non-ODF format_id should yield PASS; got {result['result']}"
        )

    def test_odf_product_source_without_spec_fact_refs_warns(self) -> None:
        """ODF PRODUCT_SOURCE item with no spec_fact_refs → WARN (blocks_sprint=False)."""
        from governance_validators import validate_spec_fact_authority_chain
        item = _product_source(format_id="fods")  # no spec_fact_refs
        result = validate_spec_fact_authority_chain(_decl([item]))
        assert result["result"] == "WARN", (
            f"ODF item without spec_fact_refs must produce WARN; got {result['result']}"
        )
        assert result.get("blocks_sprint") is False, "V37 is WARN-only — must not block sprint"

    def test_empty_declaration_passes(self) -> None:
        from governance_validators import validate_spec_fact_authority_chain
        result = validate_spec_fact_authority_chain(_decl([]))
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# V47 — validate_spec_fact_refs_in_sal_output
# ---------------------------------------------------------------------------

class TestValidateSpecFactRefsInSalOutput:
    """V47: spec_fact_refs declared in PRODUCT_SOURCE must exist in sal-facts-latest.json."""

    def test_missing_sal_file_passes(self) -> None:
        """Bootstrap tolerance: absent sal-facts-latest.json → PASS (non-blocking)."""
        from governance_validators import validate_spec_fact_refs_in_sal_output
        result = validate_spec_fact_refs_in_sal_output(
            _decl([_product_source(spec_fact_refs=["FACT-FODS-001"])]),
            repo_root=Path("/nonexistent_path_that_cannot_exist_abc123"),
        )
        assert result["result"] == "PASS", (
            f"Absent SAL file should yield PASS (bootstrap tolerance); got {result['result']}"
        )

    def test_nonexistent_fact_ref_fails(self) -> None:
        """PRODUCT_SOURCE citing a fact ID not in sal-facts-latest.json → FAIL, blocks sprint."""
        from governance_validators import validate_spec_fact_refs_in_sal_output
        sal_output = REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"
        if not sal_output.exists():
            pytest.skip("sal-facts-latest.json not present in repo")
        item = _product_source(spec_fact_refs=["FACT-NONEXISTENT-99999"])
        result = validate_spec_fact_refs_in_sal_output(_decl([item]), repo_root=REPO_ROOT)
        assert result["result"] == "FAIL", (
            f"Missing fact ref must produce FAIL; got {result['result']}"
        )
        assert result.get("blocks_sprint") is True, "V47 failure must block sprint"

    def test_no_spec_fact_refs_passes(self) -> None:
        """PRODUCT_SOURCE with no spec_fact_refs is not checked → PASS."""
        from governance_validators import validate_spec_fact_refs_in_sal_output
        result = validate_spec_fact_refs_in_sal_output(
            _decl([_product_source()]),  # no spec_fact_refs
            repo_root=REPO_ROOT,
        )
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# V51 — validate_spec_qname_coverage (in governance_validators_ext.py)
# ---------------------------------------------------------------------------

class TestValidateSpecQnameCoverage:
    """V51: Repo scan — exported classes must have spec_qname attribute."""

    def test_repo_scan_passes_after_backfill(self) -> None:
        """After TC-V53-BACKFILL-001 (commit 30b694b3), V51 must return PASS."""
        from governance_validators_ext import validate_spec_qname_coverage
        result = validate_spec_qname_coverage({}, repo_root=REPO_ROOT)
        assert result["result"] == "PASS", (
            f"V51 must be PASS after spec_qname backfill; got {result['result']}. "
            f"Items: {result.get('items', [])}"
        )

    def test_result_has_required_fields(self) -> None:
        """V51 result must have 'result', 'summary', 'items' keys."""
        from governance_validators_ext import validate_spec_qname_coverage
        result = validate_spec_qname_coverage({}, repo_root=REPO_ROOT)
        assert "result" in result
        assert "summary" in result
        assert "items" in result


# ---------------------------------------------------------------------------
# V53 — validate_spec_authority_class_completeness (in governance_validators_ext.py)
# ---------------------------------------------------------------------------

class TestValidateSpecAuthorityClassCompleteness:
    """V53: Registry python_file entries must exist and contain matching spec_qname class."""

    def test_repo_scan_returns_pass_or_warn(self) -> None:
        """V53 returns PASS or WARN (some formats may lack spec_qname classes)."""
        from governance_validators_ext import validate_spec_authority_class_completeness
        result = validate_spec_authority_class_completeness({}, repo_root=REPO_ROOT)
        assert result["result"] in ("PASS", "WARN"), (
            f"V53 should return PASS or WARN; got {result['result']}. "
            f"Items: {result.get('items', [])}"
        )

    def test_xcf_and_ndjson_no_longer_warned(self) -> None:
        """After backfill, xcf:image and ndjson:record should not appear in WARN items."""
        from governance_validators_ext import validate_spec_authority_class_completeness
        result = validate_spec_authority_class_completeness({}, repo_root=REPO_ROOT)
        warn_qnames = {i.get("qname") for i in result.get("items", [])}
        assert "xcf:image" not in warn_qnames, "xcf:image should be resolved after backfill"
        assert "ndjson:record" not in warn_qnames, "ndjson:record should be resolved after backfill"
