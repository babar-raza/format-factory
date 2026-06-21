"""
Tests for Sprint r313: ods_max_cells_per_sheet, ods_cells_exceed_sheets.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_max_cells_per_sheet, ods_cells_exceed_sheets

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


# --- ods_max_cells_per_sheet ---

def test_ods_max_cells_per_sheet_minimal_four():
    assert ods_max_cells_per_sheet(_ODS / "minimal-spreadsheet.ods") == 4


def test_ods_max_cells_per_sheet_numeric_three():
    assert ods_max_cells_per_sheet(_ODS / "numeric-row.ods") == 3


def test_ods_max_cells_per_sheet_single_one():
    assert ods_max_cells_per_sheet(_ODS / "single-cell.ods") == 1


def test_ods_max_cells_per_sheet_returns_int_minimal():
    assert isinstance(ods_max_cells_per_sheet(_ODS / "minimal-spreadsheet.ods"), int)


def test_ods_max_cells_per_sheet_returns_int_single():
    assert isinstance(ods_max_cells_per_sheet(_ODS / "single-cell.ods"), int)


def test_ods_max_cells_per_sheet_all_three_distinct():
    results = [
        ods_max_cells_per_sheet(_ODS / "minimal-spreadsheet.ods"),
        ods_max_cells_per_sheet(_ODS / "numeric-row.ods"),
        ods_max_cells_per_sheet(_ODS / "single-cell.ods"),
    ]
    assert results == [4, 3, 1]


# --- ods_cells_exceed_sheets ---

def test_ods_cells_exceed_sheets_minimal_true():
    # 4 cells > 1 sheet
    assert ods_cells_exceed_sheets(_ODS / "minimal-spreadsheet.ods") is True


def test_ods_cells_exceed_sheets_numeric_true():
    # 3 cells > 1 sheet
    assert ods_cells_exceed_sheets(_ODS / "numeric-row.ods") is True


def test_ods_cells_exceed_sheets_single_false():
    # 1 cell == 1 sheet → not strictly greater
    assert ods_cells_exceed_sheets(_ODS / "single-cell.ods") is False


def test_ods_cells_exceed_sheets_returns_bool_minimal():
    assert isinstance(ods_cells_exceed_sheets(_ODS / "minimal-spreadsheet.ods"), bool)


def test_ods_cells_exceed_sheets_returns_bool_single():
    assert isinstance(ods_cells_exceed_sheets(_ODS / "single-cell.ods"), bool)


def test_ods_cells_exceed_sheets_all_three():
    results = [
        ods_cells_exceed_sheets(_ODS / "minimal-spreadsheet.ods"),
        ods_cells_exceed_sheets(_ODS / "numeric-row.ods"),
        ods_cells_exceed_sheets(_ODS / "single-cell.ods"),
    ]
    assert results == [True, True, False]
