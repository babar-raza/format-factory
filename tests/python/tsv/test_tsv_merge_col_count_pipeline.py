"""
test_tsv_merge_col_count_pipeline.py -- TSV merge_tsv + column_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-103
Tests merge_tsv returns dict, merged row_count=4, column_count int, count=3,
merge then column_count consistent.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    merge_tsv,
    column_count,
)

_DATA_A = b"name\tdept\tscore\nAlice\teng\t90\nBob\thr\t75\n"
_DATA_B = b"name\tdept\tscore\nCarol\teng\t85\nDave\thr\t70\n"


def test_merge_tsv_returns_dict():
    result = merge_tsv(_DATA_A, _DATA_B)
    assert isinstance(result, dict)


def test_merge_tsv_row_count():
    result = merge_tsv(_DATA_A, _DATA_B)
    assert result["row_count"] == 4


def test_column_count_returns_int():
    count = column_count(_DATA_A)
    assert isinstance(count, int)


def test_column_count_correct_value():
    count = column_count(_DATA_A)
    assert count == 3


def test_merge_preserves_column_count():
    merged = merge_tsv(_DATA_A, _DATA_B)
    assert len(merged["headers"]) == 3
