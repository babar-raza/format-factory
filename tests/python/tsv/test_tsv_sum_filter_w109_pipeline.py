"""
test_tsv_sum_filter_w109_pipeline.py -- TSV sum_column_tsv + filter_rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-109
Tests sum_column_tsv returns float, correct sum, sum after filter,
filter_rows returns dict, filtered rows match value.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    sum_column_tsv,
    filter_rows,
)

_TSV_DATA = b"name\tdept\tsalary\nAlice\teng\t90000\nBob\tmkt\t70000\nCarol\teng\t85000\nDave\thr\t65000\n"


def test_sum_column_returns_float():
    result = sum_column_tsv(_TSV_DATA, "salary")
    assert isinstance(result, float)


def test_sum_column_correct_total():
    result = sum_column_tsv(_TSV_DATA, "salary")
    assert result == 310000.0


def test_sum_after_filter():
    filtered = filter_rows(_TSV_DATA, "dept", "eng")
    eng_rows = filtered["rows"]
    # Manually sum salaries for eng rows
    total = sum(float(row[2]) for row in eng_rows)
    assert total == 175000.0


def test_filter_rows_returns_dict():
    result = filter_rows(_TSV_DATA, "dept", "eng")
    assert isinstance(result, dict)


def test_filter_rows_matches_value():
    result = filter_rows(_TSV_DATA, "dept", "eng")
    names = [row[0] for row in result["rows"]]
    assert "Alice" in names
    assert "Carol" in names
    assert "Bob" not in names
