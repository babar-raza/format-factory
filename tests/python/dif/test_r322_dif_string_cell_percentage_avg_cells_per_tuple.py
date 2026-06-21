"""Tests for dif_string_cell_percentage and dif_avg_cells_per_tuple (Sprint 112, R322)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_string_cell_percentage, dif_avg_cells_per_tuple

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


def test_string_pct_minimal():
    assert abs(dif_string_cell_percentage(DIF / "minimal-2x2.dif") - 25.0) < 0.1


def test_string_pct_numeric():
    assert abs(dif_string_cell_percentage(DIF / "numeric-row.dif") - 0.0) < 0.1


def test_string_pct_single():
    assert abs(dif_string_cell_percentage(DIF / "single-cell.dif") - 0.0) < 0.1


def test_string_pct_returns_float():
    assert isinstance(dif_string_cell_percentage(DIF / "minimal-2x2.dif"), float)


def test_string_pct_nonnegative():
    assert dif_string_cell_percentage(DIF / "minimal-2x2.dif") >= 0.0


def test_avg_cells_minimal():
    assert abs(dif_avg_cells_per_tuple(DIF / "minimal-2x2.dif") - 4.0) < 0.01


def test_avg_cells_numeric():
    assert abs(dif_avg_cells_per_tuple(DIF / "numeric-row.dif") - 3.0) < 0.01


def test_avg_cells_single():
    assert abs(dif_avg_cells_per_tuple(DIF / "single-cell.dif") - 1.0) < 0.01


def test_avg_cells_returns_float():
    assert isinstance(dif_avg_cells_per_tuple(DIF / "minimal-2x2.dif"), float)


def test_avg_cells_positive():
    assert dif_avg_cells_per_tuple(DIF / "minimal-2x2.dif") > 0.0
