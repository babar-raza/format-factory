"""Tests for fods_numeric_cell_percentage and fods_avg_rows_per_sheet (Sprint 104, R314)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict
from src.python.fods.neutral_model import fods_numeric_cell_percentage, fods_avg_rows_per_sheet

FODS = _REPO / "samples" / "by-format" / "fods"


def test_numeric_pct_formula():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert abs(fods_numeric_cell_percentage(wb) - 100.0) < 0.1


def test_numeric_pct_minimal():
    wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
    assert abs(fods_numeric_cell_percentage(wb) - 0.0) < 0.1


def test_numeric_pct_typed():
    wb = parse_fods_strict(FODS / "typed-values-basic.fods")
    assert abs(fods_numeric_cell_percentage(wb) - 12.5) < 0.1


def test_numeric_pct_returns_float():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert isinstance(fods_numeric_cell_percentage(wb), float)


def test_numeric_pct_bounded():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert 0.0 <= fods_numeric_cell_percentage(wb) <= 100.0


def test_avg_rows_formula():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert abs(fods_avg_rows_per_sheet(wb) - 4.0) < 0.01


def test_avg_rows_minimal():
    wb = parse_fods_strict(FODS / "minimal-spreadsheet.fods")
    assert abs(fods_avg_rows_per_sheet(wb) - 1.0) < 0.01


def test_avg_rows_multi_sheet():
    wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
    assert abs(fods_avg_rows_per_sheet(wb) - 1.5) < 0.01


def test_avg_rows_returns_float():
    wb = parse_fods_strict(FODS / "formula-basic.fods")
    assert isinstance(fods_avg_rows_per_sheet(wb), float)


def test_avg_rows_positive():
    wb = parse_fods_strict(FODS / "multi-sheet-basic.fods")
    assert fods_avg_rows_per_sheet(wb) > 0.0
