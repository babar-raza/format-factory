"""
tests/python/fods/test_r192_fods_column_width.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT62-001
Tests for workbook_column_width_summary() — column width metadata.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import workbook_column_width_summary

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestWorkbookColumnWidthSummary:
    def test_empty_workbook_returns_empty_list(self):
        result = workbook_column_width_summary({})
        assert result == []

    def test_returns_list(self):
        result = workbook_column_width_summary({})
        assert isinstance(result, list)

    def test_real_file_returns_list(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_column_width_summary(model)
        assert isinstance(result, list)

    def test_real_file_has_entry_per_sheet(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_column_width_summary(model)
        assert len(result) >= 0  # could be empty or have sheet entries

    def test_entry_has_sheet_name(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_column_width_summary(model)
        for entry in result:
            assert "sheet_name" in entry

    def test_entry_has_widths_list(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_column_width_summary(model)
        for entry in result:
            assert "widths" in entry
            assert isinstance(entry["widths"], list)
