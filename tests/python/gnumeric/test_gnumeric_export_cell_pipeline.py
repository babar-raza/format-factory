"""
test_gnumeric_export_cell_pipeline.py -- Gnumeric export + cell accessor pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-77
Tests export_to_csv string with data, read_cell returns value, get_cell_value
returns string, count_nonempty_cells int, export_to_json parseable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    write_gnumeric,
    export_to_csv,
    read_cell,
    get_cell_value,
    count_nonempty_cells,
    export_to_json,
)


_SHEETS = [
    {
        "name": "Sheet1",
        "rows": [
            ["Alpha", "Beta"],
            ["10", "20"],
            ["30", "40"],
        ],
    }
]


def test_export_to_csv_string_with_data(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    result = export_to_csv(str(dest))
    assert isinstance(result, str)
    assert "Alpha" in result


def test_read_cell_returns_value():
    model = create_gnumeric(_SHEETS)
    result = read_cell(model, 0, 0, 0)
    assert result == "Alpha"


def test_get_cell_value_returns_string():
    model = create_gnumeric(_SHEETS)
    result = get_cell_value(model, 0, 1, 0)
    assert result == "10"


def test_count_nonempty_cells_int():
    model = create_gnumeric(_SHEETS)
    result = count_nonempty_cells(model, 0)
    assert isinstance(result, int)
    assert result == 6


def test_export_to_json_parseable(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    result = export_to_json(str(dest))
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, (dict, list))
