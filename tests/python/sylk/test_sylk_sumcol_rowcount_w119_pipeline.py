"""
test_sylk_sumcol_rowcount_w119_pipeline.py -- SYLK sum_column + get_row_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-119
Tests sum_column returns float, sum_column numeric col2=42.0,
get_row_count returns int, get_row_count correct=2,
sum_column and row_count consistent.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    sum_column,
    get_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_SLK = _SAMPLES / "minimal-2x2.slk"


def test_sum_column_returns_float():
    result = sum_column(_SLK, 2)
    assert isinstance(result, float)


def test_sum_column_numeric_value():
    result = sum_column(_SLK, 2)
    assert abs(result - 42.0) < 1e-9


def test_get_row_count_returns_int():
    result = get_row_count(_SLK)
    assert isinstance(result, int)


def test_get_row_count_correct():
    result = get_row_count(_SLK)
    assert result == 2


def test_sum_column_and_row_count_consistent():
    row_count = get_row_count(_SLK)
    col_sum = sum_column(_SLK, 2)
    assert row_count == 2 and col_sum > 0
