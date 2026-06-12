"""
test_gnumeric_row_values_fill_col_pipeline.py -- Gnumeric get_row_values + fill_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-104
Tests get_row_values returns list, first row has Q1/Q2, fill_column updates values,
fill_column returns dict, filled values accessible via get_row_values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    get_row_values,
    fill_column,
)

_SHEETS = [
    {
        "name": "Sheet1",
        "rows": [
            ["Q1", "Q2", "Q3"],
            ["10", "20", "30"],
            ["5", "15", "25"],
        ],
    }
]


def test_get_row_values_returns_list():
    model = create_gnumeric(_SHEETS)
    row = get_row_values(model, 0, 0)
    assert isinstance(row, list)


def test_get_row_values_correct_content():
    model = create_gnumeric(_SHEETS)
    row = get_row_values(model, 0, 0)
    assert "Q1" in row
    assert "Q2" in row


def test_fill_column_returns_dict():
    model = create_gnumeric(_SHEETS)
    new_model = fill_column(model, 0, 0, ["A", "B", "C"])
    assert isinstance(new_model, dict)


def test_fill_column_updates_values():
    model = create_gnumeric(_SHEETS)
    new_model = fill_column(model, 0, 0, ["X", "Y", "Z"])
    row0 = get_row_values(new_model, 0, 0)
    assert row0[0] == "X"


def test_fill_column_then_get_row_matches():
    model = create_gnumeric(_SHEETS)
    new_model = fill_column(model, 0, 2, ["100", "200", "300"])
    row1 = get_row_values(new_model, 0, 1)
    assert row1[2] == "200"
