"""
test_r58_fods_public_api.py — R58 Train F: workbook_stats in FODS public API.

Verifies that workbook_stats() is accessible from the installed package API.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-009
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


class TestFodsPublicApi:
    """workbook_stats must be accessible from the fods package public API."""

    def test_workbook_stats_importable_from_package(self):
        import fods
        assert hasattr(fods, "workbook_stats"), (
            "workbook_stats must be exported from fods package __init__.py (IV-R57-009)"
        )

    def test_workbook_stats_in_all(self):
        import fods
        assert "workbook_stats" in fods.__all__

    def test_workbook_stats_callable(self):
        import fods
        wb = {"format_id": "fods", "sheet_count": 1, "sheets": []}
        result = fods.workbook_stats(wb)
        assert isinstance(result, dict)

    def test_workbook_stats_returns_required_keys(self):
        import fods
        wb = {"format_id": "fods", "sheet_count": 2, "sheets": [
            {"name": "Sheet1", "rows": [{"cells": [{"value": "1", "data_type": "float"}]}]},
            {"name": "Sheet2", "rows": []},
        ]}
        stats = fods.workbook_stats(wb)
        required_keys = ["sheet_count", "total_rows", "total_cells", "non_empty_cells",
                         "formula_cells", "per_sheet"]
        for k in required_keys:
            assert k in stats, f"workbook_stats missing key: {k}"

    def test_workbook_stats_counts_correctly(self):
        import fods
        # Same function
        wb = {"format_id": "fods", "sheet_count": 1, "sheets": [
            {"name": "Sheet1", "rows": [
                {"cells": [
                    {"value": "hello", "data_type": "string"},
                    {"value": "=SUM(A1:A10)", "data_type": "formula"},
                ]}
            ]}
        ]}
        stats = fods.workbook_stats(wb)
        assert stats["sheet_count"] == 1
        assert stats["total_rows"] == 1
        assert stats["total_cells"] == 2
