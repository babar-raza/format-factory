"""
test_tsv_append_filter_pipeline.py -- TSV append_row + filter_rows pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-28
Tests: append_row increases row count, filter_rows exact match,
filter_rows no match returns 0, filter_rows case-insensitive,
filter_rows column value correct.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    append_row,
    count_rows,
    filter_rows,
)

_HEADERS = ["name", "dept", "score"]
_ROWS = [
    ["Alice", "eng", "90"],
    ["Bob", "mkt", "70"],
    ["Carol", "eng", "85"],
]


def _make_tsv(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    return dest


def test_append_row_increases_count(tmp_path):
    dest = _make_tsv(tmp_path)
    append_row(str(dest), ["Dave", "hr", "65"])
    assert count_rows(str(dest)) == 4


def test_filter_rows_exact_match(tmp_path):
    dest = _make_tsv(tmp_path)
    result = filter_rows(str(dest), "dept", "eng")
    assert result["row_count"] == 2


def test_filter_rows_no_match(tmp_path):
    dest = _make_tsv(tmp_path)
    result = filter_rows(str(dest), "dept", "finance")
    assert result["row_count"] == 0


def test_filter_rows_case_insensitive(tmp_path):
    dest = _make_tsv(tmp_path)
    result = filter_rows(str(dest), "dept", "ENG", case_sensitive=False)
    assert result["row_count"] == 2


def test_filter_rows_value_correct(tmp_path):
    dest = _make_tsv(tmp_path)
    result = filter_rows(str(dest), "name", "Alice")
    assert result["rows"][0][0] == "Alice"
