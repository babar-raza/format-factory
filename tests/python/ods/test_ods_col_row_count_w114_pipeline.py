"""
test_ods_col_row_count_w114_pipeline.py -- ODS get_column_count + get_row_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-114
Tests get_row_count returns int, row_count > 0, get_column_count returns int,
col_count > 0, row_count and col_count are consistent with minimal spreadsheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_ODS_FILE = _SAMPLES / "minimal-spreadsheet.ods"

from ods.ods_parser import (
    get_row_count,
    get_column_count,
)


def test_get_row_count_returns_int():
    result = get_row_count(_ODS_FILE)
    assert isinstance(result, int)


def test_get_row_count_positive():
    result = get_row_count(_ODS_FILE)
    assert result > 0


def test_get_column_count_returns_int():
    result = get_column_count(_ODS_FILE)
    assert isinstance(result, int)


def test_get_column_count_positive():
    result = get_column_count(_ODS_FILE)
    assert result > 0


def test_row_and_column_count_positive_together():
    rows = get_row_count(_ODS_FILE)
    cols = get_column_count(_ODS_FILE)
    assert rows > 0 and cols > 0
