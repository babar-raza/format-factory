"""
tests/python/fods/test_r193_fods_cell_type_matrix.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT62-001
Tests for workbook_cell_type_matrix() — cell type distribution per sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import workbook_cell_type_matrix

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestWorkbookCellTypeMatrix:
    def test_empty_workbook_returns_empty_list(self):
        result = workbook_cell_type_matrix({})
        assert result == []

    def test_returns_list(self):
        result = workbook_cell_type_matrix({})
        assert isinstance(result, list)

    def test_real_file_returns_list(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_cell_type_matrix(model)
        assert isinstance(result, list)

    def test_real_file_has_at_least_one_entry(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_cell_type_matrix(model)
        assert len(result) >= 1

    def test_entry_has_sheet_name(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_cell_type_matrix(model)
        for entry in result:
            assert "sheet_name" in entry

    def test_entry_has_by_type(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_cell_type_matrix(model)
        for entry in result:
            assert "by_type" in entry
            assert isinstance(entry["by_type"], dict)

    def test_total_cells_non_negative(self):
        from src.python.fods.parser import parse_fods
        model = parse_fods(str(SAMPLES / "minimal-spreadsheet.fods"))
        result = workbook_cell_type_matrix(model)
        for entry in result:
            assert entry.get("total_cells", 0) >= 0
