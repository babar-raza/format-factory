"""
test_tsv_max_col_drop_pipeline.py -- TSV max_column_tsv + drop_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-94
Tests max_column_tsv float, max_column_tsv correct value, drop_column returns dict,
drop_column removes header, drop then column_count decreases.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import max_column_tsv, drop_column, column_count

_TSV_DATA = b"name\tscore\trank\nAlice\t85\t2\nBob\t72\t3\nCarol\t91\t1\nDave\t68\t4\n"


def test_max_column_tsv_float(tmp_path):
    result = max_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)


def test_max_column_tsv_correct_value(tmp_path):
    result = max_column_tsv(_TSV_DATA, "score")
    assert result == 91.0


def test_drop_column_returns_dict(tmp_path):
    result = drop_column(_TSV_DATA, "rank")
    assert isinstance(result, dict)
    assert "headers" in result


def test_drop_column_removes_header(tmp_path):
    result = drop_column(_TSV_DATA, "rank")
    assert "rank" not in result["headers"]
    assert "score" in result["headers"]


def test_drop_column_count_decreases(tmp_path):
    before = column_count(_TSV_DATA)
    result = drop_column(_TSV_DATA, "rank")
    assert len(result["headers"]) == before - 1
