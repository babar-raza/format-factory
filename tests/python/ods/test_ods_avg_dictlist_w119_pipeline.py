"""
test_ods_avg_dictlist_w119_pipeline.py -- ODS average_column + get_sheet_as_dict_list pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-119
Tests average_column returns float, correct average=42.0 for Value column,
get_sheet_as_dict_list returns list, has records, first record has Name key.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    average_column,
    get_sheet_as_dict_list,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_ODS = _SAMPLES / "minimal-spreadsheet.ods"


def test_average_column_returns_float():
    result = average_column(_ODS, 1)
    assert isinstance(result, float)


def test_average_column_correct_col1():
    result = average_column(_ODS, 1)
    assert abs(result - 42.0) < 1e-9


def test_get_sheet_as_dict_list_returns_list():
    result = get_sheet_as_dict_list(_ODS)
    assert isinstance(result, list)


def test_get_sheet_as_dict_list_has_records():
    result = get_sheet_as_dict_list(_ODS)
    assert len(result) >= 1


def test_get_sheet_as_dict_list_has_name_key():
    result = get_sheet_as_dict_list(_ODS)
    assert "Name" in result[0]
