"""
test_tsv_min_col_get_col_pipeline.py -- TSV min_column_tsv + get_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-97
Tests min_column_tsv float, min correct value, get_column returns list,
get_column count=4, get_column has expected value.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import min_column_tsv, get_column

_TSV_DATA = b"name\tscore\tdept\nAlice\t85\teng\nBob\t72\thr\nCarol\t91\teng\nDave\t68\thr\n"


def test_min_column_tsv_float(tmp_path):
    result = min_column_tsv(_TSV_DATA, "score")
    assert isinstance(result, float)


def test_min_column_tsv_correct_value(tmp_path):
    result = min_column_tsv(_TSV_DATA, "score")
    assert result == 68.0


def test_get_column_returns_list(tmp_path):
    result = get_column(_TSV_DATA, "name")
    assert isinstance(result, list)


def test_get_column_count(tmp_path):
    result = get_column(_TSV_DATA, "name")
    assert len(result) == 4


def test_get_column_has_expected_value(tmp_path):
    result = get_column(_TSV_DATA, "name")
    assert "Alice" in result
    assert "Carol" in result
