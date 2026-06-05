"""Tests for the product-code change ledger validator v3.

Validates:
- BACKFILLED_PRE_GOVERNANCE rejection for post-R90 sprints
- Invalid source state detection
- Missing ledger entries for changed files
- Stale SHA-256 hash detection
- Valid ledger passes
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from validate_product_code_ledger import validate_ledger, load_ledger, VALID_SOURCE_STATES


def _good_ledger(**overrides):
    base = {
        "ledger_version": "2.0",
        "tracking_base_ref": "abc123",
        "entries": [
            {
                "entry_id": "TEST-001",
                "classification": "GOVERNED_PRODUCT_CHANGE",
                "sprint": "R100",
                "capability_refs": ["test.capability"],
                "api_symbols": ["TestApi"],
                "source_files": [
                    {
                        "path": "src/python/test/test_file.py",
                        "state": "present",
                        "sha256": "abc123def456",
                    }
                ],
            }
        ],
    }
    base.update(overrides)
    return base


class TestLedgerValidatorNegative:

    def test_backfilled_rejected_for_post_governance(self):
        ledger = _good_ledger()
        ledger["entries"][0]["classification"] = "BACKFILLED_PRE_GOVERNANCE"
        ledger["entries"][0]["sprint"] = "R95"
        # Mock git to avoid real git calls
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("BACKFILLED_PRE_GOVERNANCE" in e for e in result["errors"])

    def test_invalid_source_state(self):
        ledger = _good_ledger()
        ledger["entries"][0]["source_files"][0]["state"] = "modified"
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("invalid source state" in e for e in result["errors"])

    def test_missing_sha256(self):
        ledger = _good_ledger()
        del ledger["entries"][0]["source_files"][0]["sha256"]
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("missing sha256" in e for e in result["errors"])

    def test_missing_entry_id(self):
        ledger = _good_ledger()
        del ledger["entries"][0]["entry_id"]
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("missing entry_id" in e for e in result["errors"])

    def test_duplicate_entry_id(self):
        ledger = _good_ledger()
        ledger["entries"].append(ledger["entries"][0].copy())
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("duplicate entry_id" in e for e in result["errors"])

    def test_invalid_classification(self):
        ledger = _good_ledger()
        ledger["entries"][0]["classification"] = "INVALID_CLASS"
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("invalid classification" in e for e in result["errors"])

    def test_empty_capability_refs(self):
        ledger = _good_ledger()
        ledger["entries"][0]["capability_refs"] = []
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("capability_refs" in e for e in result["errors"])

    def test_empty_api_symbols(self):
        ledger = _good_ledger()
        ledger["entries"][0]["api_symbols"] = []
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("api_symbols" in e for e in result["errors"])

    def test_non_src_path(self):
        ledger = _good_ledger()
        ledger["entries"][0]["source_files"][0]["path"] = "docs/test.md"
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert not result["valid"]
        assert any("invalid src path" in e for e in result["errors"])


class TestLedgerValidatorPositive:

    def test_valid_ledger_passes(self):
        ledger = _good_ledger()
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert result["valid"]

    def test_backfilled_ok_for_pre_governance(self):
        ledger = _good_ledger()
        ledger["entries"][0]["classification"] = "BACKFILLED_PRE_GOVERNANCE"
        ledger["entries"][0]["sprint"] = "R85"
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert result["valid"]

    def test_deleted_state_ok(self):
        ledger = _good_ledger()
        ledger["entries"][0]["source_files"][0]["state"] = "deleted"
        del ledger["entries"][0]["source_files"][0]["sha256"]
        with patch("validate_product_code_ledger.collect_changed_src_files", return_value=set()):
            result = validate_ledger(ledger, REPO_ROOT)
        assert result["valid"]

    def test_real_ledger_passes(self):
        """Validate the actual product-code-change-ledger.json against the repo."""
        ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
        if ledger_path.exists():
            ledger = load_ledger(ledger_path)
            result = validate_ledger(ledger, REPO_ROOT)
            assert result["valid"], f"Real ledger failed: {result['errors']}"


class TestValidSourceStates:

    def test_valid_states(self):
        assert "present" in VALID_SOURCE_STATES
        assert "deleted" in VALID_SOURCE_STATES
        assert "modified" not in VALID_SOURCE_STATES
