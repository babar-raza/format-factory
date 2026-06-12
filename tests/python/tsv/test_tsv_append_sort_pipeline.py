"""
test_tsv_append_sort_pipeline.py -- TSV append + sort pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-58
Tests append_row increases row count, sort_rows ascending, sort_rows descending,
append_rows in-memory, sort_rows preserves headers.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    append_row,
    append_rows,
    sort_rows,
    count_rows,
    write_tsv,
)

_HEADERS = ["name", "score"]
_ROWS = [["Alice", "90"], ["Dave", "60"], ["Carol", "80"], ["Bob", "70"]]


def _write_tsv(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    return dest


def test_append_row_increases_count(tmp_path):
    dest = _write_tsv(tmp_path)
    append_row(str(dest), ["Eve", "85"])
    count = count_rows(str(dest))
    assert count == 5


def test_sort_rows_ascending(tmp_path):
    dest = _write_tsv(tmp_path)
    result = sort_rows(str(dest), "name")
    names = [row[0] for row in result["rows"]]
    assert names[0] == "Alice"
    assert names[-1] == "Dave"


def test_sort_rows_descending(tmp_path):
    dest = _write_tsv(tmp_path)
    result = sort_rows(str(dest), "score", reverse=True)
    scores = [row[1] for row in result["rows"]]
    assert scores[0] == "90"


def test_append_rows_in_memory(tmp_path):
    dest = _write_tsv(tmp_path)
    result = append_rows(str(dest), [["Frank", "95"], ["Grace", "55"]])
    assert result["row_count"] == 6


def test_sort_rows_preserves_headers(tmp_path):
    dest = _write_tsv(tmp_path)
    result = sort_rows(str(dest), "name")
    assert result["headers"] == _HEADERS
