"""Tests for FODS workbook_get_column_values.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT24-001
Covers: column value extraction from FODS workbooks
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import workbook_get_column_values


def _make_wb(sheets_data):
    """Build a minimal FODS workbook dict from list of (name, rows_list) tuples."""
    sheets = []
    for name, rows_data in sheets_data:
        rows = []
        for row_vals in rows_data:
            cells = [{"value": v, "type": "string" if isinstance(v, str) else "float"} for v in row_vals]
            rows.append({"cells": cells})
        sheets.append({"name": name, "rows": rows})
    return {"sheets": sheets}


class TestWorkbookGetColumnValues:
    def test_first_column(self):
        wb = _make_wb([("S1", [["Name", "Age"], ["Alice", "30"], ["Bob", "25"]])])
        vals = workbook_get_column_values(wb, 0)
        assert vals == ["Name", "Alice", "Bob"]

    def test_second_column(self):
        wb = _make_wb([("S1", [["Name", "Age"], ["Alice", "30"]])])
        vals = workbook_get_column_values(wb, 1)
        assert vals == ["Age", "30"]

    def test_out_of_range_column(self):
        wb = _make_wb([("S1", [["A", "B"], ["C", "D"]])])
        vals = workbook_get_column_values(wb, 5)
        assert all(v is None for v in vals)
        assert len(vals) == 2

    def test_bad_sheet_index(self):
        wb = _make_wb([("S1", [["A"]])])
        vals = workbook_get_column_values(wb, 0, sheet_index=5)
        assert vals == []

    def test_second_sheet(self):
        wb = _make_wb([
            ("S1", [["First"]]),
            ("S2", [["Second"]]),
        ])
        vals = workbook_get_column_values(wb, 0, sheet_index=1)
        assert vals == ["Second"]

    def test_empty_sheet(self):
        wb = _make_wb([("Empty", [])])
        vals = workbook_get_column_values(wb, 0)
        assert vals == []

    def test_ragged_rows(self):
        wb = _make_wb([("S1", [["A", "B", "C"], ["X"]])])
        vals = workbook_get_column_values(wb, 2)
        assert vals[0] == "C"
        assert vals[1] is None

    def test_no_sheets(self):
        wb = {"sheets": []}
        vals = workbook_get_column_values(wb, 0)
        assert vals == []
