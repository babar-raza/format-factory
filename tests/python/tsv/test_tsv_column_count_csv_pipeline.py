"""
test_tsv_column_count_csv_pipeline.py -- TSV column_count + to_csv pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-88
Tests column_count int, column_count=3, to_csv returns string,
to_csv has comma separator, to_csv has data content.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import column_count, to_csv

_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t85\nBob\thr\t72\nCarol\teng\t91\n"


def test_column_count_int(tmp_path):
    count = column_count(_TSV_DATA)
    assert isinstance(count, int)


def test_column_count_value(tmp_path):
    count = column_count(_TSV_DATA)
    assert count == 3


def test_to_csv_returns_string(tmp_path):
    result = to_csv(_TSV_DATA)
    assert isinstance(result, str)


def test_to_csv_has_comma_separator(tmp_path):
    result = to_csv(_TSV_DATA)
    assert "," in result


def test_to_csv_has_data_content(tmp_path):
    result = to_csv(_TSV_DATA)
    assert "Alice" in result
    assert "eng" in result
