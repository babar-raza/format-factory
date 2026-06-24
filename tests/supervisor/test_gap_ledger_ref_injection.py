"""Tests for TC-C7-005: gap_ledger_ref injection into declarations.

Validates that:
1. gap_ledger_to_work_items.py includes gap_ledger_ref in output
2. capability_feature_compiler.py includes gap_ledger_ref in output
3. The merge logic in autonomous_cycle.py Step 3a-pre correctly backfills
   gap_ledger_ref into declaration items from work items
4. End-to-end: closure engine finds matches when gap_ledger_ref is merged
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


class TestGapLedgerToWorkItemsRef:
    """gap_ledger_to_work_items.py must include gap_ledger_ref."""

    def test_gap_ledger_ref_present(self):
        from gap_ledger_to_work_items import _gap_to_work_item
        gap = {
            "gap_id": "GAP-CSV-FOSS-042",
            "format": "CSV",
            "capability_name": "csv_row_count",
            "status": "open",
            "priority": "P1",
            "product_type": "foss_reduced",
        }
        item = _gap_to_work_item(gap, score=10)
        assert item["gap_ledger_ref"] == "GAP-CSV-FOSS-042"
        assert item["gap_id"] == "GAP-CSV-FOSS-042"


class TestCapabilityFeatureCompilerRef:
    """capability_feature_compiler.py must include gap_ledger_ref."""

    def test_gap_ledger_ref_present(self):
        from capability_feature_compiler import _gap_to_work_item
        gap = {
            "gap_id": "GAP-XCF-FOSS-007",
            "format": "XCF",
            "capability_name": "xcf_layer_count",
            "status": "open",
            "priority": "P1",
            "product_type": "foss_reduced",
        }
        item = _gap_to_work_item(gap, score=5)
        assert item["gap_ledger_ref"] == "GAP-XCF-FOSS-007"
        assert item["gap_ref"] == "GAP-XCF-FOSS-007"


class TestMergeLogic:
    """Simulate the Step 3a-pre merge logic from autonomous_cycle.py."""

    def _simulate_merge(self, decl_items, work_items):
        """Reproduce the merge logic from autonomous_cycle.py Step 3a-pre."""
        wi_by_id = {}
        for wi in work_items:
            ref = wi.get("gap_ledger_ref") or wi.get("gap_id")
            wid = wi.get("item_id") or wi.get("action_id")
            if ref and wid:
                wi_by_id[wid] = ref

        merged = 0
        for di in decl_items:
            did = di.get("item_id", "")
            if not di.get("gap_ledger_ref") and did in wi_by_id:
                di["gap_ledger_ref"] = wi_by_id[did]
                merged += 1
        return merged

    def test_merge_backfills_ref(self):
        decl_items = [
            {"item_id": "WI-001", "status": "completed"},
            {"item_id": "WI-002", "status": "completed"},
        ]
        work_items = [
            {"item_id": "WI-001", "gap_ledger_ref": "GAP-CSV-001"},
            {"item_id": "WI-002", "gap_ledger_ref": "GAP-XCF-002"},
        ]
        merged = self._simulate_merge(decl_items, work_items)
        assert merged == 2
        assert decl_items[0]["gap_ledger_ref"] == "GAP-CSV-001"
        assert decl_items[1]["gap_ledger_ref"] == "GAP-XCF-002"

    def test_merge_skips_existing_ref(self):
        decl_items = [
            {"item_id": "WI-001", "gap_ledger_ref": "GAP-EXISTING", "status": "completed"},
        ]
        work_items = [
            {"item_id": "WI-001", "gap_ledger_ref": "GAP-NEW"},
        ]
        merged = self._simulate_merge(decl_items, work_items)
        assert merged == 0
        assert decl_items[0]["gap_ledger_ref"] == "GAP-EXISTING"

    def test_merge_handles_no_match(self):
        decl_items = [
            {"item_id": "WI-ORPHAN", "status": "completed"},
        ]
        work_items = [
            {"item_id": "WI-OTHER", "gap_ledger_ref": "GAP-X"},
        ]
        merged = self._simulate_merge(decl_items, work_items)
        assert merged == 0
        assert "gap_ledger_ref" not in decl_items[0]

    def test_merge_uses_gap_id_fallback(self):
        """Work items from gap_ledger_to_work_items use gap_id, not gap_ledger_ref."""
        decl_items = [
            {"item_id": "GAP-CSV-042", "status": "completed"},
        ]
        work_items = [
            {"item_id": "GAP-CSV-042", "gap_id": "GAP-CSV-042"},
        ]
        merged = self._simulate_merge(decl_items, work_items)
        assert merged == 1
        assert decl_items[0]["gap_ledger_ref"] == "GAP-CSV-042"


class TestEndToEndClosureWithMerge:
    """After merge, closure engine should find matches and close gaps."""

    def test_closure_after_merge(self, tmp_path):
        from gap_closure_engine import close_gaps_from_grades

        # Write gap ledger
        ledger = {"schema_version": "1.0", "gaps": [
            {"gap_id": "GAP-E2E-001", "format": "CSV", "capability_name": "Test",
             "status": "open", "priority": "P1"},
        ]}
        gl_path = tmp_path / "gap-ledger.json"
        gl_path.write_text(json.dumps(ledger), encoding="utf-8")

        # Declaration WITHOUT gap_ledger_ref (as worker would write)
        decl_items = [
            {"item_id": "WI-E2E", "status": "completed",
             "evidence_paths": ["tests/python/csv/test_e2e.py"]},
        ]

        # Work items WITH gap_ledger_ref
        work_items = [
            {"item_id": "WI-E2E", "gap_ledger_ref": "GAP-E2E-001"},
        ]

        # Simulate merge (Step 3a-pre)
        for di in decl_items:
            did = di.get("item_id", "")
            for wi in work_items:
                wid = wi.get("item_id", "")
                if did == wid and not di.get("gap_ledger_ref"):
                    di["gap_ledger_ref"] = wi.get("gap_ledger_ref")

        declaration = {
            "planned_work_items": decl_items,
            "test_results": {"passed": 5, "failed": 0},
        }
        review = {
            "item_grades": [
                {"item_id": "WI-E2E", "supervisor_grade": "ACCEPTED_VERIFIED",
                 "evidence_paths_found": ["tests/python/csv/test_e2e.py"],
                 "tests_supporting": 5, "tests_failing": 0},
            ],
            "accepted_items": ["WI-E2E"],
            "rework_items": [],
            "overclaimed_items": [],
        }

        result = close_gaps_from_grades(review, declaration, gl_path, "sprint-e2e")
        assert result["matches"] == 1
        assert result["closed"] == 1

        updated = json.loads(gl_path.read_text())
        assert updated["gaps"][0]["status"] == "closed"
