"""
test_tsv_filter_row_key_pipeline.py -- TSV filter_rows + get_row_by_key pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-85
Tests filter_rows returns dict, filter_rows count=2, filter_rows exact match,
get_row_by_key returns list, get_row_by_key not found returns None.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import filter_rows, get_row_by_key

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t85\nBob\thr\t72\nCarol\teng\t91\nDave\thr\t68\n"


def test_filter_rows_returns_dict(tmp_path):
    result = filter_rows(_TSV_DATA, "dept", "eng")
    assert isinstance(result, dict)
    assert "rows" in result


def test_filter_rows_count(tmp_path):
    result = filter_rows(_TSV_DATA, "dept", "eng")
    assert len(result["rows"]) == 2


def test_filter_rows_exact_match(tmp_path):
    result = filter_rows(_TSV_DATA, "dept", "hr")
    for row in result["rows"]:
        assert row[1] == "hr"


def test_get_row_by_key_returns_list(tmp_path):
    row = get_row_by_key(_TSV_DATA, "name", "Alice")
    assert isinstance(row, list)
    assert "Alice" in row


def test_get_row_by_key_not_found_none(tmp_path):
    row = get_row_by_key(_TSV_DATA, "name", "Zara")
    assert row is None
