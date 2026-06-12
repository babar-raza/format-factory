"""
test_tsv_advanced_ops.py -- TSV advanced operations deepening.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-12
Tests average_column_tsv, sort_rows, add_column, drop_column, filter_rows
with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    average_column_tsv,
    sort_rows,
    add_column,
    drop_column,
    filter_rows,
    rename_column,
)

# name\tscore\tdept rows
_TSV_BYTES = b"name\tscore\tdept\nAlice\t90\teng\nBob\t75\tmkt\nCarol\t85\teng\nDave\t60\tmkt\n"


def test_average_column_tsv_correct():
    avg = average_column_tsv(_TSV_BYTES, "score")
    assert abs(avg - 77.5) < 0.001


def test_sort_rows_ascending():
    result = sort_rows(_TSV_BYTES, "score")
    hdrs = result["headers"]
    idx = hdrs.index("score")
    scores = [row[idx] for row in result["rows"]]
    assert scores[0] == "60"
    assert scores[-1] == "90"


def test_sort_rows_descending():
    result = sort_rows(_TSV_BYTES, "score", reverse=True)
    hdrs = result["headers"]
    idx = hdrs.index("score")
    scores = [row[idx] for row in result["rows"]]
    assert scores[0] == "90"
    assert scores[-1] == "60"


def test_add_column_appears_in_headers():
    result = add_column(_TSV_BYTES, "level", ["A", "B", "C", "D"])
    assert "level" in result["headers"]


def test_add_column_values_correct():
    result = add_column(_TSV_BYTES, "level", ["A", "B", "C", "D"])
    hdrs = result["headers"]
    idx = hdrs.index("level")
    vals = [row[idx] for row in result["rows"]]
    assert vals == ["A", "B", "C", "D"]


def test_drop_column_removes_field():
    result = drop_column(_TSV_BYTES, "dept")
    assert "dept" not in result["headers"]


def test_filter_rows_by_dept():
    result = filter_rows(_TSV_BYTES, "dept", "eng")
    hdrs = result["headers"]
    idx = hdrs.index("name")
    names = [row[idx] for row in result["rows"]]
    assert "Alice" in names
    assert "Carol" in names
    assert "Bob" not in names


def test_rename_column_updates_header():
    result = rename_column(_TSV_BYTES, "name", "full_name")
    assert "full_name" in result["headers"]
    assert "name" not in result["headers"]
