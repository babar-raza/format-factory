"""
test_tsv_sample_rows_pipeline.py -- TSV sample rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-67
Tests sample_rows returns dict, sample_rows count, sample_rows headers preserved,
sum_column_tsv float, sample_rows n=1.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    sample_rows,
    sum_column_tsv,
)

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t90\nBob\tmkt\t70\nCarol\teng\t80\nDave\thr\t60\n"


def test_sample_rows_returns_dict():
    result = sample_rows(_TSV_DATA, 2)
    assert isinstance(result, dict)


def test_sample_rows_count():
    result = sample_rows(_TSV_DATA, 3)
    assert len(result["rows"]) == 3


def test_sample_rows_headers_preserved():
    result = sample_rows(_TSV_DATA, 2)
    assert result["headers"] == ["name", "dept", "score"]


def test_sum_column_tsv_float():
    total = sum_column_tsv(_TSV_DATA, "score")
    assert isinstance(total, float)
    assert total == 300.0


def test_sample_rows_n_one():
    result = sample_rows(_TSV_DATA, 1)
    assert len(result["rows"]) == 1
    assert result["rows"][0][0] == "Alice"
