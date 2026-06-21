"""Tests for dif_numeric_cell_percentage and dif_cells_per_row (Sprint 103, R313)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_numeric_cell_percentage, dif_cells_per_row

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


def test_numeric_pct_minimal():
    assert abs(dif_numeric_cell_percentage(DIF / "minimal-2x2.dif") - 25.0) < 0.1


def test_numeric_pct_numeric_row():
    assert abs(dif_numeric_cell_percentage(DIF / "numeric-row.dif") - 100.0) < 0.1


def test_numeric_pct_single():
    assert abs(dif_numeric_cell_percentage(DIF / "single-cell.dif") - 100.0) < 0.1


def test_numeric_pct_returns_float():
    assert isinstance(dif_numeric_cell_percentage(DIF / "minimal-2x2.dif"), float)


def test_numeric_pct_bounded():
    pct = dif_numeric_cell_percentage(DIF / "minimal-2x2.dif")
    assert 0.0 <= pct <= 100.0


def test_cells_per_row_minimal():
    assert abs(dif_cells_per_row(DIF / "minimal-2x2.dif") - 8.0) < 0.01


def test_cells_per_row_numeric():
    assert abs(dif_cells_per_row(DIF / "numeric-row.dif") - 3.0) < 0.01


def test_cells_per_row_single():
    assert abs(dif_cells_per_row(DIF / "single-cell.dif") - 1.0) < 0.01


def test_cells_per_row_returns_float():
    assert isinstance(dif_cells_per_row(DIF / "minimal-2x2.dif"), float)


def test_cells_per_row_positive():
    assert dif_cells_per_row(DIF / "numeric-row.dif") > 0.0
