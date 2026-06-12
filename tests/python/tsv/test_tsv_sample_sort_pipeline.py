"""
test_tsv_sample_sort_pipeline.py -- TSV sample_rows + sort_rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-34
Tests sample_rows count, sort_rows ascending, sort_rows descending,
rename_column persists, add_column new column values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    sample_rows,
    sort_rows,
    rename_column,
    add_column,
)

_HEADERS = ["name", "score"]
_ROWS = [
    ["Alice", "90"],
    ["Bob", "70"],
    ["Carol", "85"],
    ["Dave", "95"],
    ["Eve", "60"],
]


def _make_tsv(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    return dest


def test_sample_rows_count(tmp_path):
    dest = _make_tsv(tmp_path)
    result = sample_rows(str(dest), 3)
    assert len(result["rows"]) == 3


def test_sort_rows_ascending(tmp_path):
    dest = _make_tsv(tmp_path)
    result = sort_rows(str(dest), "name")
    assert result["rows"][0][0] == "Alice"


def test_sort_rows_descending(tmp_path):
    dest = _make_tsv(tmp_path)
    result = sort_rows(str(dest), "name", reverse=True)
    assert result["rows"][0][0] == "Eve"


def test_rename_column(tmp_path):
    dest = _make_tsv(tmp_path)
    result = rename_column(str(dest), "score", "points")
    assert "points" in result["headers"]
    assert "score" not in result["headers"]


def test_add_column_values(tmp_path):
    dest = _make_tsv(tmp_path)
    result = add_column(str(dest), "grade", ["A", "B", "B", "A", "C"])
    assert "grade" in result["headers"]
    assert result["rows"][0][-1] == "A"
