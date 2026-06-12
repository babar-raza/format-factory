"""
test_tsv_numeric_ops_pipeline.py -- TSV numeric operations pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-73
Tests median_column_tsv float, std_column_tsv float, get_numeric_columns list,
min_column_tsv float, sum_column_tsv float.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    load_tsv,
    median_column_tsv,
    std_column_tsv,
    get_numeric_columns,
    min_column_tsv,
    sum_column_tsv,
)

_TSV_DATA = b"name\tscore\tage\nAlice\t80\t25\nBob\t60\t30\nCarol\t90\t28\nDave\t70\t35\n"


def test_median_column_float():
    result = median_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)
    assert result == 75.0


def test_std_column_float():
    result = std_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)
    assert result > 0.0


def test_get_numeric_columns_list():
    data = load_tsv(_TSV_DATA)
    result = get_numeric_columns(data)
    assert isinstance(result, list)
    assert "score" in result
    assert "age" in result


def test_min_column_float():
    result = min_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)
    assert result == 60.0


def test_sum_column_float():
    result = sum_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)
    assert result == 300.0
