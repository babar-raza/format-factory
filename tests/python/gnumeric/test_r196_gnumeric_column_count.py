"""Tests for gnumeric_column_count — rnext65 product deepening."""
from pathlib import Path

GNUMERIC_DIR = Path("samples/by-format/gnumeric")


def test_import():
    from src.python.gnumeric import gnumeric_column_count
    assert callable(gnumeric_column_count)


def test_minimal_spreadsheet_has_one_column():
    from src.python.gnumeric import gnumeric_column_count, load
    m = load(GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
    assert gnumeric_column_count(m, 0) == 1


def test_multi_cell_has_two_columns():
    from src.python.gnumeric import gnumeric_column_count, load
    m = load(GNUMERIC_DIR / "multi-cell-basic.gnumeric")
    assert gnumeric_column_count(m, 0) == 2


def test_empty_sheet_returns_zero():
    from src.python.gnumeric import gnumeric_column_count, load
    m = load(GNUMERIC_DIR / "empty-sheet.gnumeric")
    assert gnumeric_column_count(m, 0) == 0


def test_returns_int():
    from src.python.gnumeric import gnumeric_column_count, load
    m = load(GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
    assert isinstance(gnumeric_column_count(m, 0), int)


def test_invalid_sheet_index_returns_zero():
    from src.python.gnumeric import gnumeric_column_count, load
    m = load(GNUMERIC_DIR / "minimal-spreadsheet.gnumeric")
    assert gnumeric_column_count(m, 99) == 0
