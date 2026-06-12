"""
test_gnumeric_extract_row_count_pipeline.py -- Gnumeric extract_values + row_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-95
Tests extract_values from file returns list, row_count int, row_count correct value,
extract_values contains data, row_count after add_sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    write_gnumeric,
    extract_values,
    row_count,
    add_sheet,
)

_SHEETS = [
    {
        "name": "Data",
        "rows": [
            ["Alice", "85"],
            ["Bob", "72"],
            ["Carol", "91"],
        ],
    }
]


def test_extract_values_from_file_returns_list(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    result = extract_values(str(dest))
    assert isinstance(result, list)


def test_row_count_int(tmp_path):
    model = create_gnumeric(_SHEETS)
    count = row_count(model, 0)
    assert isinstance(count, int)


def test_row_count_correct_value(tmp_path):
    model = create_gnumeric(_SHEETS)
    count = row_count(model, 0)
    assert count == 3


def test_extract_values_contains_data(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    result = extract_values(str(dest))
    assert "Alice" in result or len(result) > 0


def test_row_count_second_sheet(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = add_sheet(model, "Extra")
    count = row_count(model, 1)
    assert isinstance(count, int)
    assert count == 0
