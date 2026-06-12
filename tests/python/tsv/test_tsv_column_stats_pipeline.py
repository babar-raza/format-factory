"""
test_tsv_column_stats_pipeline.py -- TSV column stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-46
Tests median_column_tsv, std_column_tsv, average_column_tsv, min_column_tsv,
max_column_tsv on a numeric dataset.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    median_column_tsv,
    std_column_tsv,
    average_column_tsv,
    min_column_tsv,
    max_column_tsv,
)

_ROWS = [
    ["name", "score"],
    ["Alice", "60"],
    ["Bob", "70"],
    ["Carol", "80"],
    ["Dave", "90"],
    ["Eve", "100"],
]


def _write(tmp_path):
    path = tmp_path / "scores.tsv"
    write_tsv(_ROWS, str(path))
    return path


def test_average_column_tsv(tmp_path):
    path = _write(tmp_path)
    avg = average_column_tsv(str(path), "score")
    assert avg == 80.0


def test_median_column_tsv(tmp_path):
    path = _write(tmp_path)
    med = median_column_tsv(str(path), "score")
    assert med == 80.0


def test_min_column_tsv(tmp_path):
    path = _write(tmp_path)
    mn = min_column_tsv(str(path), "score")
    assert mn == 60.0


def test_max_column_tsv(tmp_path):
    path = _write(tmp_path)
    mx = max_column_tsv(str(path), "score")
    assert mx == 100.0


def test_std_column_tsv(tmp_path):
    path = _write(tmp_path)
    std = std_column_tsv(str(path), "score")
    assert round(std, 1) == 14.1
