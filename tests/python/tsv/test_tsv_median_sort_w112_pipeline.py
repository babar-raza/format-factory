"""
test_tsv_median_sort_w112_pipeline.py -- TSV median_column_tsv + sort_rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-112
Tests median returns float, correct median, sort_rows returns dict,
sorted rows are ordered, sort combined with median.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    median_column_tsv,
    sort_rows,
)

_TSV_DATA = b"name\tscore\nAlice\t80\nBob\t90\nCarol\t70\nDave\t60\n"


def test_median_returns_float():
    result = median_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)


def test_median_correct_value():
    # Sorted: 60, 70, 80, 90 → median = (70+80)/2 = 75.0
    result = median_column_tsv(_TSV_DATA, "score")
    assert result == 75.0


def test_sort_rows_returns_dict():
    result = sort_rows(_TSV_DATA, "score")
    assert isinstance(result, dict)


def test_sort_rows_ordered():
    result = sort_rows(_TSV_DATA, "score")
    scores = [float(row[1]) for row in result["rows"]]
    assert scores == sorted(scores)


def test_sort_then_median_consistent():
    sorted_result = sort_rows(_TSV_DATA, "score")
    # After sort, median should still be 75.0
    import io
    tsv_bytes = ("name\tscore\n" + "\n".join(
        "\t".join(row) for row in sorted_result["rows"]
    ) + "\n").encode()
    med = median_column_tsv(tsv_bytes, "score")
    assert med == 75.0
