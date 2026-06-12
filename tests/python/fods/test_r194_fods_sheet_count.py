"""Tests for fods_sheet_count — rnext63 product deepening."""
from pathlib import Path

FODS_DIR = Path("samples/by-format/fods")


def test_import():
    from src.python.fods import fods_sheet_count
    assert callable(fods_sheet_count)


def test_minimal_spreadsheet_has_one_sheet():
    from src.python.fods import fods_sheet_count, parse_fods
    m = parse_fods(FODS_DIR / "minimal-spreadsheet.fods")
    assert fods_sheet_count(m) == 1


def test_multi_sheet_has_two_sheets():
    from src.python.fods import fods_sheet_count, parse_fods
    m = parse_fods(FODS_DIR / "multi-sheet-basic.fods")
    assert fods_sheet_count(m) == 2


def test_formula_basic_has_one_sheet():
    from src.python.fods import fods_sheet_count, parse_fods
    m = parse_fods(FODS_DIR / "formula-basic.fods")
    assert fods_sheet_count(m) == 1


def test_returns_int():
    from src.python.fods import fods_sheet_count, parse_fods
    m = parse_fods(FODS_DIR / "minimal-spreadsheet.fods")
    assert isinstance(fods_sheet_count(m), int)


def test_empty_workbook_returns_zero():
    from src.python.fods import fods_sheet_count
    assert fods_sheet_count({}) == 0
