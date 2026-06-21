"""Tests for fods_total_numeric_cell_count and fods_avg_string_per_sheet (Sprint 97, R307)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_total_numeric_cell_count, fods_avg_string_per_sheet

FODS = _REPO / "samples" / "by-format" / "fods"


def test_total_numeric_cell_count_formula():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert fods_total_numeric_cell_count(wb) == 4


def test_total_numeric_cell_count_minimal():
    wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
    assert fods_total_numeric_cell_count(wb) == 0


def test_total_numeric_cell_count_typed():
    wb = parse_fods_strict(FODS / "typed-values-basic.fods")
    assert fods_total_numeric_cell_count(wb) == 1


def test_total_numeric_cell_count_returns_int():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert isinstance(fods_total_numeric_cell_count(wb), int)


def test_total_numeric_cell_count_nonnegative():
    wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
    assert fods_total_numeric_cell_count(wb) >= 0


def test_avg_string_per_sheet_formula():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert abs(fods_avg_string_per_sheet(wb) - 0.0) < 0.01


def test_avg_string_per_sheet_minimal():
    wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
    assert abs(fods_avg_string_per_sheet(wb) - 1.0) < 0.01


def test_avg_string_per_sheet_multi():
    wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
    assert abs(fods_avg_string_per_sheet(wb) - 2.5) < 0.01


def test_avg_string_per_sheet_returns_float():
    wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
    assert isinstance(fods_avg_string_per_sheet(wb), float)


def test_avg_string_per_sheet_nonnegative():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert fods_avg_string_per_sheet(wb) >= 0.0
