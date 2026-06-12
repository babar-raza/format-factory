"""
test_tsv_column_drop_pipeline.py -- TSV column count + drop pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-61
Tests column_count int, drop_column removes column, get_column list,
rename_column changes header, get_column_values list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    column_count,
    drop_column,
    get_column,
    rename_column,
    get_column_values,
)

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t90\nBob\tmkt\t70\nCarol\teng\t80\n"


def test_column_count_int():
    count = column_count(_TSV_DATA)
    assert count == 3


def test_drop_column_removes_column():
    result = drop_column(_TSV_DATA, "dept")
    assert "dept" not in result["headers"]
    assert len(result["headers"]) == 2


def test_get_column_list():
    result = get_column(_TSV_DATA, "name")
    assert isinstance(result, list)
    assert "Alice" in result


def test_rename_column_changes_header():
    result = rename_column(_TSV_DATA, "score", "points")
    assert "points" in result["headers"]
    assert "score" not in result["headers"]


def test_get_column_values_list():
    result = get_column_values(_TSV_DATA, "dept")
    assert isinstance(result, list)
    assert "eng" in result
