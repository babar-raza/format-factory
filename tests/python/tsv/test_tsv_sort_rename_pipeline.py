"""
test_tsv_sort_rename_pipeline.py -- TSV sort_rows + rename_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-82
Tests sort_rows ascending, sort_rows descending, rename_column changes header,
sort_rows returns dict, rename_column rows preserved.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import sort_rows, rename_column

_TSV_DATA = b"name\tscore\nAlice\t80\nBob\t60\nCarol\t90\nDave\t70\n"


def test_sort_rows_ascending(tmp_path):
    result = sort_rows(_TSV_DATA, "score")
    rows = result["rows"]
    scores = [int(r[1]) for r in rows]
    assert scores == sorted(scores)


def test_sort_rows_descending(tmp_path):
    result = sort_rows(_TSV_DATA, "score", reverse=True)
    rows = result["rows"]
    scores = [int(r[1]) for r in rows]
    assert scores == sorted(scores, reverse=True)


def test_sort_rows_returns_dict(tmp_path):
    result = sort_rows(_TSV_DATA, "name")
    assert isinstance(result, dict)
    assert "rows" in result


def test_rename_column_changes_header(tmp_path):
    result = rename_column(_TSV_DATA, "score", "points")
    assert "points" in result["headers"]
    assert "score" not in result["headers"]


def test_rename_column_rows_preserved(tmp_path):
    result = rename_column(_TSV_DATA, "name", "player")
    assert len(result["rows"]) == 4
