"""
test_dif_sumrow_sumcol_w116_pipeline.py -- DIF sum_row + sum_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-116
Tests sum_row returns float, sum_row correct value=6.0,
sum_column returns float, sum_column correct value=1.0 for col 0,
sum of all columns equals sum_row value.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    sum_row,
    sum_column,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"
_DIF = _SAMPLES / "numeric-row.dif"


def test_sum_row_returns_float():
    result = sum_row(_DIF, 0)
    assert isinstance(result, float)


def test_sum_row_correct_value():
    result = sum_row(_DIF, 0)
    assert abs(result - 6.0) < 1e-9


def test_sum_column_returns_float():
    result = sum_column(_DIF, 0)
    assert isinstance(result, float)


def test_sum_column_correct_col0():
    result = sum_column(_DIF, 0)
    assert abs(result - 1.0) < 1e-9


def test_sum_columns_equal_sum_row():
    col0 = sum_column(_DIF, 0)
    col1 = sum_column(_DIF, 1)
    col2 = sum_column(_DIF, 2)
    row_total = sum_row(_DIF, 0)
    assert abs((col0 + col1 + col2) - row_total) < 1e-9
