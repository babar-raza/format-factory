"""Tests for TC-GUARD-001 bootstrap exemption (GOVERNANCE_ASSET item_type).

Verifies that guard_001_checker.py correctly:
1. Exempts GOVERNANCE_ASSET items from the gap-reference check
2. Still enforces check for PRODUCT_SOURCE and PRODUCT_TEST
3. Correctly identifies violations (missing gap refs)
4. Passes items that have gap refs
"""
import sys
from pathlib import Path

import pytest

# Ensure tools/supervisor is on path for import
_REPO = Path(__file__).parent.parent.parent
_SUP = _REPO / "tools" / "supervisor"
if str(_SUP) not in sys.path:
    sys.path.insert(0, str(_SUP))

from guard_001_checker import (
    check_guard_001,
    check_guard_001_all,
    is_guard_001_exempt,
    EXEMPT_ITEM_TYPES,
    CHECKED_ITEM_TYPES,
)


class TestIsGuard001Exempt:
    def test_governance_asset_is_exempt(self):
        assert is_guard_001_exempt({"item_type": "GOVERNANCE_ASSET"}) is True

    def test_product_source_not_exempt(self):
        assert is_guard_001_exempt({"item_type": "PRODUCT_SOURCE"}) is False

    def test_product_test_not_exempt(self):
        assert is_guard_001_exempt({"item_type": "PRODUCT_TEST"}) is False

    def test_governance_taskcard_not_exempt(self):
        assert is_guard_001_exempt({"item_type": "GOVERNANCE_TASKCARD"}) is False

    def test_missing_item_type_not_exempt(self):
        assert is_guard_001_exempt({}) is False

    def test_exempt_types_set_contains_governance_asset(self):
        assert "GOVERNANCE_ASSET" in EXEMPT_ITEM_TYPES

    def test_checked_types_set(self):
        assert "PRODUCT_SOURCE" in CHECKED_ITEM_TYPES
        assert "PRODUCT_TEST" in CHECKED_ITEM_TYPES
        assert "GOVERNANCE_ASSET" not in CHECKED_ITEM_TYPES


class TestCheckGuard001:
    def test_governance_asset_exempt_no_violation(self):
        item = {"item_type": "GOVERNANCE_ASSET", "item_id": "TC-GOV-001"}
        result = check_guard_001(item)
        assert result["exempt"] is True
        assert result["violation"] is False

    def test_product_source_with_gap_ref_passes(self):
        item = {
            "item_type": "PRODUCT_SOURCE",
            "item_id": "TC-SRC-001",
            "gap_ledger_ref": "GAP-FODT-001",
        }
        result = check_guard_001(item)
        assert result["exempt"] is False
        assert result["violation"] is False

    def test_product_source_with_capability_ref_passes(self):
        item = {
            "item_type": "PRODUCT_SOURCE",
            "item_id": "TC-SRC-002",
            "capability_ref": "FODT-LOAD-001",
        }
        result = check_guard_001(item)
        assert result["violation"] is False

    def test_product_source_with_spec_fact_refs_passes(self):
        item = {
            "item_type": "PRODUCT_SOURCE",
            "item_id": "TC-SRC-003",
            "spec_fact_refs": ["FACT-FODT-001"],
        }
        result = check_guard_001(item)
        assert result["violation"] is False

    def test_product_source_no_refs_is_violation(self):
        item = {"item_type": "PRODUCT_SOURCE", "item_id": "TC-SRC-BAD"}
        result = check_guard_001(item)
        assert result["exempt"] is False
        assert result["violation"] is True

    def test_product_test_no_refs_is_violation(self):
        item = {"item_type": "PRODUCT_TEST", "item_id": "TC-TEST-BAD"}
        result = check_guard_001(item)
        assert result["violation"] is True

    def test_governance_taskcard_not_checked(self):
        item = {"item_type": "GOVERNANCE_TASKCARD", "item_id": "TC-GOV-TASKCARD"}
        result = check_guard_001(item)
        assert result["exempt"] is False
        assert result["violation"] is False

    def test_unknown_item_type_not_checked(self):
        item = {"item_type": "UNKNOWN_TYPE", "item_id": "TC-UNKNOWN"}
        result = check_guard_001(item)
        assert result["violation"] is False


class TestCheckGuard001All:
    def test_empty_list_returns_empty(self):
        assert check_guard_001_all([]) == []

    def test_all_exempt_returns_empty(self):
        items = [
            {"item_type": "GOVERNANCE_ASSET", "item_id": "A"},
            {"item_type": "GOVERNANCE_ASSET", "item_id": "B"},
        ]
        assert check_guard_001_all(items) == []

    def test_product_source_with_refs_passes(self):
        items = [
            {"item_type": "PRODUCT_SOURCE", "item_id": "PS-OK", "gap_ledger_ref": "GAP-001"},
        ]
        assert check_guard_001_all(items) == []

    def test_product_source_without_refs_is_violation(self):
        items = [
            {"item_type": "PRODUCT_SOURCE", "item_id": "PS-BAD"},
        ]
        assert check_guard_001_all(items) == ["PS-BAD"]

    def test_mixed_items_only_violations_returned(self):
        items = [
            {"item_type": "GOVERNANCE_ASSET", "item_id": "GOV-OK"},
            {"item_type": "PRODUCT_SOURCE", "item_id": "PS-OK", "gap_ledger_ref": "GAP-001"},
            {"item_type": "PRODUCT_SOURCE", "item_id": "PS-BAD"},
            {"item_type": "PRODUCT_TEST", "item_id": "PT-BAD"},
        ]
        result = check_guard_001_all(items)
        assert "PS-BAD" in result
        assert "PT-BAD" in result
        assert "GOV-OK" not in result
        assert "PS-OK" not in result
        assert len(result) == 2

    def test_governance_asset_without_gap_ref_still_exempt(self):
        """GOVERNANCE_ASSET items are ALWAYS exempt, even with no gap_ledger_ref."""
        items = [
            {"item_type": "GOVERNANCE_ASSET", "item_id": "GOV-NO-REF"},
        ]
        assert check_guard_001_all(items) == []
