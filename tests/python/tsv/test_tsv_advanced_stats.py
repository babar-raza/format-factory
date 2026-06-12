"""
test_tsv_advanced_stats.py -- TSV advanced statistics functions.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-26
Tests min_column_tsv, max_column_tsv, average_column_tsv,
median_column_tsv, std_column_tsv on a numeric column.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    min_column_tsv,
    max_column_tsv,
    average_column_tsv,
    median_column_tsv,
    std_column_tsv,
)

_HEADERS = ["name", "score"]
_ROWS = [
    ["Alice", "90"],
    ["Bob", "70"],
    ["Carol", "80"],
    ["Dave", "100"],
    ["Eve", "60"],
]


def _write_tsv(tmp_path):
    dest = tmp_path / "stats.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    return dest


def test_min_column_tsv_score(tmp_path):
    dest = _write_tsv(tmp_path)
    assert min_column_tsv(str(dest), "score") == 60.0


def test_max_column_tsv_score(tmp_path):
    dest = _write_tsv(tmp_path)
    assert max_column_tsv(str(dest), "score") == 100.0


def test_average_column_tsv_score(tmp_path):
    dest = _write_tsv(tmp_path)
    assert average_column_tsv(str(dest), "score") == 80.0


def test_median_column_tsv_score(tmp_path):
    dest = _write_tsv(tmp_path)
    assert median_column_tsv(str(dest), "score") == 80.0


def test_std_column_tsv_score(tmp_path):
    dest = _write_tsv(tmp_path)
    std = std_column_tsv(str(dest), "score")
    # population std of [60,70,80,90,100] = 14.142...
    assert round(std, 1) == 14.1
