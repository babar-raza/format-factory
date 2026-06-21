"""
r319 ODS analytics: ods_total_cells_minus_sheets, ods_has_multi_row_sheet.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_total_cells_minus_sheets, ods_has_multi_row_sheet

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


# --- ods_total_cells_minus_sheets ---

def test_total_cells_minus_sheets_minimal_spreadsheet():
    assert ods_total_cells_minus_sheets(_ODS / "minimal-spreadsheet.ods") == 3

def test_total_cells_minus_sheets_numeric_row():
    assert ods_total_cells_minus_sheets(_ODS / "numeric-row.ods") == 2

def test_total_cells_minus_sheets_single_cell():
    assert ods_total_cells_minus_sheets(_ODS / "single-cell.ods") == 0

def test_total_cells_minus_sheets_returns_int():
    result = ods_total_cells_minus_sheets(_ODS / "minimal-spreadsheet.ods")
    assert isinstance(result, int)

def test_total_cells_minus_sheets_minimal_greater_than_single():
    assert ods_total_cells_minus_sheets(_ODS / "minimal-spreadsheet.ods") > ods_total_cells_minus_sheets(_ODS / "single-cell.ods")

def test_total_cells_minus_sheets_nonnegative():
    for name in ["minimal-spreadsheet.ods", "numeric-row.ods", "single-cell.ods"]:
        assert ods_total_cells_minus_sheets(_ODS / name) >= 0


# --- ods_has_multi_row_sheet ---

def test_has_multi_row_sheet_minimal_spreadsheet_true():
    assert ods_has_multi_row_sheet(_ODS / "minimal-spreadsheet.ods") is True

def test_has_multi_row_sheet_numeric_row_false():
    assert ods_has_multi_row_sheet(_ODS / "numeric-row.ods") is False

def test_has_multi_row_sheet_single_cell_false():
    assert ods_has_multi_row_sheet(_ODS / "single-cell.ods") is False

def test_has_multi_row_sheet_returns_bool():
    result = ods_has_multi_row_sheet(_ODS / "minimal-spreadsheet.ods")
    assert isinstance(result, bool)

def test_has_multi_row_sheet_numeric_row_is_bool():
    result = ods_has_multi_row_sheet(_ODS / "numeric-row.ods")
    assert isinstance(result, bool)

def test_has_multi_row_sheet_only_minimal_true():
    results = [
        ods_has_multi_row_sheet(_ODS / "minimal-spreadsheet.ods"),
        ods_has_multi_row_sheet(_ODS / "numeric-row.ods"),
        ods_has_multi_row_sheet(_ODS / "single-cell.ods"),
    ]
    assert results.count(True) == 1
