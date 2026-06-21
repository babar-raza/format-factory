"""Tests for dif_nonempty_column_count and dif_avg_numeric_per_row (Sprint 98, R308)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_nonempty_column_count, dif_avg_numeric_per_row

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"


def test_nonempty_column_count_minimal():
    assert dif_nonempty_column_count(DIF / "minimal-2x2.dif") == 8


def test_nonempty_column_count_numeric_row():
    assert dif_nonempty_column_count(DIF / "numeric-row.dif") == 3


def test_nonempty_column_count_single():
    assert dif_nonempty_column_count(DIF / "single-cell.dif") == 1


def test_nonempty_column_count_returns_int():
    assert isinstance(dif_nonempty_column_count(DIF / "minimal-2x2.dif"), int)


def test_nonempty_column_count_positive():
    assert dif_nonempty_column_count(DIF / "minimal-2x2.dif") > 0


def test_avg_numeric_per_row_minimal():
    assert abs(dif_avg_numeric_per_row(DIF / "minimal-2x2.dif") - 2.0) < 0.01


def test_avg_numeric_per_row_numeric_row():
    assert abs(dif_avg_numeric_per_row(DIF / "numeric-row.dif") - 3.0) < 0.01


def test_avg_numeric_per_row_single():
    assert abs(dif_avg_numeric_per_row(DIF / "single-cell.dif") - 1.0) < 0.01


def test_avg_numeric_per_row_returns_float():
    assert isinstance(dif_avg_numeric_per_row(DIF / "minimal-2x2.dif"), float)


def test_avg_numeric_per_row_nonnegative():
    assert dif_avg_numeric_per_row(DIF / "single-cell.dif") >= 0.0
