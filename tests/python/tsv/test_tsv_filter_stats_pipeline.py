"""
test_tsv_filter_stats_pipeline.py -- TSV filter + column stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-55
Tests filter_rows returns dict, filter_rows row_count, filter_rows rows content,
average_column_tsv, max_column_tsv.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    filter_rows,
    average_column_tsv,
    max_column_tsv,
)

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t90\nBob\tmkt\t70\nCarol\teng\t80\nDave\thr\t60\n"


def test_filter_rows_returns_dict():
    result = filter_rows(_TSV_DATA, "dept", "eng")
    assert isinstance(result, dict)


def test_filter_rows_row_count():
    result = filter_rows(_TSV_DATA, "dept", "eng")
    assert result["row_count"] == 2


def test_filter_rows_content():
    result = filter_rows(_TSV_DATA, "dept", "eng")
    names = [row[0] for row in result["rows"]]
    assert "Alice" in names
    assert "Carol" in names


def test_average_column_tsv():
    avg = average_column_tsv(_TSV_DATA, "score")
    assert avg == 75.0


def test_max_column_tsv():
    max_val = max_column_tsv(_TSV_DATA, "score")
    assert max_val == 90.0
