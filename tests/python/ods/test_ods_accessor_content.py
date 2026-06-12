"""
test_ods_accessor_content.py -- ODS accessor content verification with exact values.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-15
Tests get_cell_value, get_row_values, get_column_values, get_all_values,
get_sheet_names, count_sheets with exact content assertions from real samples.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import (
    get_all_values,
    get_cell_value,
    get_row_values,
    get_column_values,
    get_row_count,
    get_column_count,
    get_sheet_names,
    count_sheets,
)

_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")


def test_cell_value_header_name():
    assert get_cell_value(_MINIMAL, 0, 0, 0) == "Name"


def test_cell_value_header_value():
    assert get_cell_value(_MINIMAL, 0, 0, 1) == "Value"


def test_cell_value_data_name():
    assert get_cell_value(_MINIMAL, 0, 1, 0) == "Alpha"


def test_cell_value_data_number():
    val = get_cell_value(_MINIMAL, 0, 1, 1)
    assert float(val) == 42.0


def test_row_values_header():
    row = get_row_values(_MINIMAL, 0, 0)
    assert row[0] == "Name"
    assert row[1] == "Value"


def test_row_values_data():
    row = get_row_values(_MINIMAL, 0, 1)
    assert row[0] == "Alpha"


def test_column_values_name_column():
    col = get_column_values(_MINIMAL, 0)
    assert "Name" in col
    assert "Alpha" in col


def test_all_values_contains_all():
    vals = get_all_values(_MINIMAL)
    assert "Name" in vals
    assert "Value" in vals
    assert "Alpha" in vals


def test_sheet_names_returns_list():
    names = get_sheet_names(_MINIMAL)
    assert isinstance(names, list)
    assert "Sheet1" in names


def test_count_sheets_is_one():
    assert count_sheets(_MINIMAL) == 1


def test_row_count_is_two():
    assert get_row_count(_MINIMAL) == 2


def test_column_count_is_two():
    assert get_column_count(_MINIMAL) == 2
