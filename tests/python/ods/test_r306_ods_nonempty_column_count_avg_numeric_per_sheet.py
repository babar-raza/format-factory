"""Tests for ods_nonempty_column_count and ods_avg_numeric_per_sheet (Sprint 96, R306)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_nonempty_column_count, ods_avg_numeric_per_sheet

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


def test_nonempty_column_count_minimal():
    assert ods_nonempty_column_count(ODS / "minimal-spreadsheet.ods") == 2


def test_nonempty_column_count_numeric_row():
    assert ods_nonempty_column_count(ODS / "numeric-row.ods") == 3


def test_nonempty_column_count_single():
    assert ods_nonempty_column_count(ODS / "single-cell.ods") == 1


def test_nonempty_column_count_returns_int():
    assert isinstance(ods_nonempty_column_count(ODS / "minimal-spreadsheet.ods"), int)


def test_nonempty_column_count_positive():
    assert ods_nonempty_column_count(ODS / "minimal-spreadsheet.ods") > 0


def test_avg_numeric_per_sheet_minimal():
    assert abs(ods_avg_numeric_per_sheet(ODS / "minimal-spreadsheet.ods") - 1.0) < 0.01


def test_avg_numeric_per_sheet_numeric_row():
    assert abs(ods_avg_numeric_per_sheet(ODS / "numeric-row.ods") - 3.0) < 0.01


def test_avg_numeric_per_sheet_single():
    assert abs(ods_avg_numeric_per_sheet(ODS / "single-cell.ods") - 0.0) < 0.01


def test_avg_numeric_per_sheet_returns_float():
    assert isinstance(ods_avg_numeric_per_sheet(ODS / "minimal-spreadsheet.ods"), float)


def test_avg_numeric_per_sheet_nonnegative():
    assert ods_avg_numeric_per_sheet(ODS / "single-cell.ods") >= 0.0
