"""
test_gnumeric_sheet_rows_pipeline.py -- Gnumeric get_sheet_as_rows pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-74
Tests get_sheet_as_rows returns list of lists, row count, cell content,
get_row_count int, get_sheet_count int.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    get_sheet_as_rows,
    get_row_count,
    get_sheet_count,
    write_gnumeric,
    load,
)


_SHEETS = [
    {
        "name": "Report",
        "rows": [
            ["Header1", "Header2", "Header3"],
            ["A", "B", "C"],
            ["X", "Y", "Z"],
        ],
    }
]


def test_get_sheet_as_rows_returns_list():
    model = create_gnumeric(_SHEETS)
    result = get_sheet_as_rows(model, 0)
    assert isinstance(result, list)


def test_get_sheet_as_rows_row_count():
    model = create_gnumeric(_SHEETS)
    result = get_sheet_as_rows(model, 0)
    assert len(result) == 3


def test_get_sheet_as_rows_cell_content():
    model = create_gnumeric(_SHEETS)
    result = get_sheet_as_rows(model, 0)
    assert result[0][0] == "Header1"
    assert result[2][2] == "Z"


def test_get_row_count_int():
    model = create_gnumeric(_SHEETS)
    result = get_row_count(model, 0)
    assert isinstance(result, int)
    assert result == 3


def test_get_sheet_count_int(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    loaded = load(str(dest))
    result = get_sheet_count(str(dest))
    assert isinstance(result, int)
    assert result == 1
