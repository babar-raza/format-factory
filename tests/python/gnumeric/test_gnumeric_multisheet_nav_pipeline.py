"""
test_gnumeric_multisheet_nav_pipeline.py -- Gnumeric multisheet navigation pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-80
Tests get_sheet_by_name dict, get_sheet_index int, sheet_names list,
get_row returns list, get_column returns list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    add_sheet,
    get_sheet_by_name,
    get_sheet_index,
    sheet_names,
    get_row,
    get_column,
)


_SHEETS = [
    {
        "name": "Alpha",
        "rows": [
            ["X", "Y", "Z"],
            ["1", "2", "3"],
            ["4", "5", "6"],
        ],
    },
    {
        "name": "Beta",
        "rows": [
            ["P", "Q"],
            ["7", "8"],
        ],
    },
]


def test_get_sheet_by_name_returns_dict(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = get_sheet_by_name(model, "Alpha")
    assert isinstance(result, dict)


def test_get_sheet_index_int(tmp_path):
    model = create_gnumeric(_SHEETS)
    idx = get_sheet_index(model, "Beta")
    assert isinstance(idx, int)
    assert idx == 1


def test_sheet_names_list(tmp_path):
    model = create_gnumeric(_SHEETS)
    names = sheet_names(model)
    assert isinstance(names, list)
    assert "Alpha" in names
    assert "Beta" in names


def test_get_row_returns_list(tmp_path):
    model = create_gnumeric(_SHEETS)
    row = get_row(model, 0, 0)
    assert isinstance(row, list)
    assert row[0] == "X"


def test_get_column_returns_list(tmp_path):
    model = create_gnumeric(_SHEETS)
    col = get_column(model, 0, 0)
    assert isinstance(col, list)
    assert "X" in col
