"""Tests for spec-parity governance validators (V_SPEC_QNAME, V_SKELETON,
V_SPEC_PARITY_GATE, V_DEPTH_FIELDS).

Lane 2 of system-hardening sprint.
"""
from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from governance_validators import (
    validate_spec_qname_refs,
    validate_skeleton_progress,
    validate_spec_parity_gate,
    validate_implementation_depth_fields,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decl(*items):
    return {"planned_work_items": list(items)}


def _product_item(**kw):
    base = {
        "item_id": "PS-001",
        "item_type": "PRODUCT_SOURCE",
        "title": "Test product item",
        "status": "completed",
    }
    base.update(kw)
    return base


def _release_gate_item(**kw):
    base = {
        "item_id": "RG-001",
        "item_type": "RELEASE_GATE",
        "title": "Gate item",
        "status": "completed",
    }
    base.update(kw)
    return base


# ===================================================================
# V_SPEC_QNAME tests
# ===================================================================

class TestValidateSpecQnameRefs:
    """V_SPEC_QNAME validator tests."""

    def test_product_source_with_qname_refs_passes(self):
        """Product source item with spec_qname_refs passes."""
        item = _product_item(
            spec_qname_refs=["FODS-FACT-001", "FODS-FACT-002"],
            changed_files=["src/python/fods/fods_parser.py"],
        )
        result = validate_spec_qname_refs(_decl(item))
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_odf_model_item_without_qname_refs_warns(self):
        """Product source touching ODF model path without spec_qname_refs gets WARN."""
        item = _product_item(
            changed_files=["src/python/fods/fods_parser.py"],
        )
        result = validate_spec_qname_refs(_decl(item))
        assert result["result"] == "WARN"
        assert len(result["items"]) == 1
        assert "ODF" in result["items"][0]["issue"]

    def test_release_gate_without_qname_refs_fails(self):
        """RELEASE_GATE item without spec_qname_refs gets FAIL."""
        item = _release_gate_item()
        result = validate_spec_qname_refs(_decl(item))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_non_odf_product_source_passes_without_qname(self):
        """Product source not touching ODF paths passes without qname refs."""
        item = _product_item(
            changed_files=["src/python/csv/csv_parser.py"],
        )
        result = validate_spec_qname_refs(_decl(item))
        assert result["result"] == "PASS"

    def test_release_gate_with_qname_refs_passes(self):
        """RELEASE_GATE item WITH spec_qname_refs passes."""
        item = _release_gate_item(
            spec_qname_refs=["ODS-FACT-001"],
        )
        result = validate_spec_qname_refs(_decl(item))
        assert result["result"] == "PASS"


# ===================================================================
# V_SKELETON tests
# ===================================================================

class TestValidateSkeletonProgress:
    """V_SKELETON validator tests."""

    def test_skeleton_only_evidence_warns(self):
        """Item with only __init__.py evidence gets WARN."""
        item = _product_item(
            evidence_paths=["src/python/fods/__init__.py"],
        )
        result = validate_skeleton_progress(_decl(item))
        assert result["result"] == "WARN"
        assert result["items"][0]["issue"] == "skeleton_only"

    def test_replayable_claim_skeleton_fails(self):
        """Item with replayable claim + skeleton evidence FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a tiny file (< 10 lines)
            tiny = Path(tmpdir) / "tiny.py"
            tiny.write_text("# stub\n", encoding="utf-8")

            item = _product_item(
                evidence_paths=[str(tiny.relative_to(Path(tmpdir)))],
                claim_classification="REPLAYABLE_NOT_YET_REPLAYED",
            )
            result = validate_skeleton_progress(
                _decl(item), repo_root=Path(tmpdir)
            )
            assert result["result"] == "FAIL"
            assert "replayable" in result["items"][0]["issue"].lower()

    def test_substantial_evidence_passes(self):
        """Item with substantial evidence (>=10 lines) passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            big = Path(tmpdir) / "parser.py"
            big.write_text("\n".join(f"line {i}" for i in range(20)), encoding="utf-8")

            item = _product_item(
                evidence_paths=[str(big.relative_to(Path(tmpdir)))],
            )
            result = validate_skeleton_progress(
                _decl(item), repo_root=Path(tmpdir)
            )
            assert result["result"] == "PASS"


# ===================================================================
# V_SPEC_PARITY_GATE tests
# ===================================================================

class TestValidateSpecParityGate:
    """V_SPEC_PARITY_GATE validator tests."""

    def test_release_gate_without_parity_results_fails(self):
        """RELEASE_GATE without spec_parity_validator_results gets FAIL."""
        item = _release_gate_item()
        result = validate_spec_parity_gate(_decl(item))
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert "spec_parity_validator_results" in result["items"][0]["missing_fields"]

    def test_non_gate_item_passes_without_parity_fields(self):
        """Non-gate item passes V_SPEC_PARITY_GATE without those fields."""
        item = _product_item()
        result = validate_spec_parity_gate(_decl(item))
        assert result["result"] == "PASS"

    def test_release_gate_with_both_fields_passes(self):
        """RELEASE_GATE with both fields passes."""
        item = _release_gate_item(
            spec_parity_validator_results={"status": "ok"},
            depth_validator_results={"depth": 3},
        )
        result = validate_spec_parity_gate(_decl(item))
        assert result["result"] == "PASS"


# ===================================================================
# V_DEPTH_FIELDS tests
# ===================================================================

class TestValidateImplementationDepthFields:
    """V_DEPTH_FIELDS validator tests."""

    def test_product_source_without_depth_score_warns(self):
        """Product source without implementation_depth_score gets WARN."""
        item = _product_item()
        result = validate_implementation_depth_fields(_decl(item))
        assert result["result"] == "WARN"
        assert any(
            "implementation_depth_score" in w.get("missing_fields", [])
            for w in result["items"]
        )

    def test_product_source_with_all_depth_fields_passes(self):
        """Product source with all depth fields passes."""
        item = _product_item(
            implementation_depth_score=0.85,
            tests_supporting=["test_foo.py::test_bar"],
        )
        result = validate_implementation_depth_fields(_decl(item))
        assert result["result"] == "PASS"

    def test_non_product_source_ignored(self):
        """Non-PRODUCT_SOURCE items are not checked."""
        item = {
            "item_id": "GOV-001",
            "item_type": "GOVERNANCE_DOC",
            "title": "Doc",
        }
        result = validate_implementation_depth_fields(_decl(item))
        assert result["result"] == "PASS"
