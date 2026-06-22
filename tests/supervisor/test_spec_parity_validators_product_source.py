"""TC-VALIDATOR-PROD-TEST-001: Integration tests for spec-parity validators
against realistic PRODUCT_SOURCE and RELEASE_GATE declaration items.

Tests validate_spec_qname_refs, validate_spec_parity_gate, and validate_skeleton_progress
at their enforcement boundaries — confirming behavior for both compliant and non-compliant
declarations.

Validators operate on declaration["planned_work_items"], not top-level declaration fields.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import (  # noqa: E402
    validate_spec_qname_refs,
    validate_spec_parity_gate,
    validate_skeleton_progress,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ODF_MODEL_FILE = "src/python/fodt/spec/table/table_cell.py"


def _decl_with_items(items: list[dict]) -> dict:
    """Build a minimal declaration dict wrapping a list of planned_work_items."""
    return {
        "planned_work_items": items,
        "changed_files": [],
    }


def _product_source_item(
    item_id: str = "TC-TEST-001",
    spec_qname_refs: list[str] | None = None,
    changed_files: list[str] | None = None,
    touched_files: list[str] | None = None,
) -> dict:
    item: dict = {
        "item_id": item_id,
        "item_type": "PRODUCT_SOURCE",
        "title": "Test product source item",
    }
    if spec_qname_refs is not None:
        item["spec_qname_refs"] = spec_qname_refs
    if changed_files is not None:
        item["changed_files"] = changed_files
    if touched_files is not None:
        item["touched_files"] = touched_files
    return item


def _release_gate_item(
    item_id: str = "TC-GATE-001",
    spec_qname_refs: list[str] | None = None,
    spec_parity_validator_results: dict | None = None,
    depth_validator_results: dict | None = None,
) -> dict:
    item: dict = {
        "item_id": item_id,
        "item_type": "RELEASE_GATE",
        "title": "Test release gate item",
    }
    if spec_qname_refs is not None:
        item["spec_qname_refs"] = spec_qname_refs
    if spec_parity_validator_results is not None:
        item["spec_parity_validator_results"] = spec_parity_validator_results
    if depth_validator_results is not None:
        item["depth_validator_results"] = depth_validator_results
    return item


# ---------------------------------------------------------------------------
# validate_spec_qname_refs
# ---------------------------------------------------------------------------

class TestValidateSpecQnameRefs:
    """PRODUCT_SOURCE touching ODF paths without spec_qname_refs → WARN;
    RELEASE_GATE without spec_qname_refs → FAIL."""

    def test_product_source_odf_path_no_qname_refs_gives_warn(self):
        """PRODUCT_SOURCE touching ODF model path with no spec_qname_refs must WARN."""
        decl = _decl_with_items([
            _product_source_item(changed_files=[ODF_MODEL_FILE]),
        ])
        result = validate_spec_qname_refs(decl)
        assert result["result"] == "WARN", (
            f"Expected WARN for PRODUCT_SOURCE touching ODF path without spec_qname_refs, "
            f"got: {result['result']} — {result.get('message')}"
        )

    def test_product_source_odf_path_with_qname_refs_passes(self):
        """PRODUCT_SOURCE touching ODF model path WITH spec_qname_refs must PASS."""
        decl = _decl_with_items([
            _product_source_item(
                changed_files=[ODF_MODEL_FILE],
                spec_qname_refs=["table:table-cell"],
            ),
        ])
        result = validate_spec_qname_refs(decl)
        assert result["result"] == "PASS", (
            f"Expected PASS for PRODUCT_SOURCE with spec_qname_refs, got: {result['result']}"
        )

    def test_product_source_non_odf_path_no_qname_passes(self):
        """PRODUCT_SOURCE NOT touching ODF model paths passes even without spec_qname_refs."""
        decl = _decl_with_items([
            _product_source_item(changed_files=["tests/python/fodt/test_something.py"]),
        ])
        result = validate_spec_qname_refs(decl)
        assert result["result"] == "PASS", (
            f"Non-ODF PRODUCT_SOURCE should PASS without spec_qname_refs, got: {result['result']}"
        )

    def test_release_gate_no_qname_refs_gives_fail(self):
        """RELEASE_GATE without spec_qname_refs must FAIL (blocking)."""
        decl = _decl_with_items([
            _release_gate_item(spec_qname_refs=None),
        ])
        result = validate_spec_qname_refs(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for RELEASE_GATE without spec_qname_refs, got: {result['result']}"
        )
        assert result.get("blocks_sprint") is True, (
            "RELEASE_GATE spec_qname_refs failure must block sprint"
        )

    def test_release_gate_with_qname_refs_passes(self):
        """RELEASE_GATE with spec_qname_refs must PASS."""
        decl = _decl_with_items([
            _release_gate_item(spec_qname_refs=["table:table-cell", "table:table-row"]),
        ])
        result = validate_spec_qname_refs(decl)
        assert result["result"] == "PASS", (
            f"Expected PASS for RELEASE_GATE with spec_qname_refs, got: {result['result']}"
        )

    def test_empty_planned_items_passes(self):
        """Declaration with no planned_work_items must PASS (vacuous)."""
        result = validate_spec_qname_refs({"planned_work_items": []})
        assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# validate_spec_parity_gate
# ---------------------------------------------------------------------------

class TestValidateSpecParityGate:
    """RELEASE_GATE items missing spec_parity_validator_results or depth_validator_results → FAIL."""

    def test_release_gate_missing_both_fields_gives_fail(self):
        """RELEASE_GATE without spec_parity_validator_results and depth_validator_results → FAIL."""
        decl = _decl_with_items([
            _release_gate_item(
                spec_parity_validator_results=None,
                depth_validator_results=None,
            ),
        ])
        result = validate_spec_parity_gate(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL for RELEASE_GATE missing parity/depth results, got: {result['result']}"
        )
        assert result.get("blocks_sprint") is True

    def test_release_gate_missing_depth_gives_fail(self):
        """RELEASE_GATE with parity results but missing depth_validator_results → FAIL."""
        decl = _decl_with_items([
            _release_gate_item(
                spec_parity_validator_results={"all_pass": True},
                depth_validator_results=None,
            ),
        ])
        result = validate_spec_parity_gate(decl)
        assert result["result"] == "FAIL", (
            f"Expected FAIL when depth_validator_results missing, got: {result['result']}"
        )

    def test_release_gate_with_both_fields_passes(self):
        """RELEASE_GATE with both required fields populated → PASS."""
        decl = _decl_with_items([
            _release_gate_item(
                spec_parity_validator_results={"all_pass": True, "validators": []},
                depth_validator_results={"score": 0.8},
            ),
        ])
        result = validate_spec_parity_gate(decl)
        assert result["result"] == "PASS", (
            f"Expected PASS for RELEASE_GATE with both fields, got: {result['result']}"
        )

    def test_product_source_item_is_skipped(self):
        """PRODUCT_SOURCE items must be ignored (pass unconditionally) by this validator."""
        decl = _decl_with_items([
            _product_source_item(),  # no parity/depth fields
        ])
        result = validate_spec_parity_gate(decl)
        assert result["result"] == "PASS", (
            f"PRODUCT_SOURCE items must pass unconditionally, got: {result['result']}"
        )

    def test_empty_planned_items_passes(self):
        """Declaration with no items must PASS (vacuous)."""
        result = validate_spec_parity_gate({"planned_work_items": []})
        assert result["result"] == "PASS"
