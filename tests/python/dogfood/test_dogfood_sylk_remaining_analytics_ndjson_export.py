"""
Dogfood pipeline: SYLK remaining analytics → NDJSON export.
Covers: sylk_has_numeric_cells, sylk_data_density, sylk_is_single_row,
        sylk_max_string_length, find_value, find_rows_by_value
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    sylk_has_numeric_cells,
    sylk_data_density,
    sylk_is_single_row,
    sylk_max_string_length,
    find_value,
    find_rows_by_value,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _valid_sylk_files():
    return sorted(_SYLK_DIR.glob("*.slk"))


def _minimal_slk():
    return str(next(f for f in _valid_sylk_files() if "minimal" in f.name))


def test_sylk_has_numeric_cells(tmp_path):
    path = _minimal_slk()
    result = sylk_has_numeric_cells(path)
    assert isinstance(result, bool)
    assert result is True  # minimal-2x2.slk has numeric cell (42)

    record = {"format": "sylk", "function": "sylk_has_numeric_cells", "has_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["has_numeric"] is True
    assert json.dumps(loaded[0]) is not None


def test_sylk_data_density(tmp_path):
    path = _minimal_slk()
    density = sylk_data_density(path)
    assert isinstance(density, float)
    assert 0.0 <= density <= 1.0

    record = {"format": "sylk", "function": "sylk_data_density", "density": density}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_sylk_is_single_row(tmp_path):
    path = _minimal_slk()
    result = sylk_is_single_row(path)
    assert isinstance(result, bool)
    assert result is False  # minimal-2x2.slk has 2 rows

    record = {"format": "sylk", "function": "sylk_is_single_row", "is_single_row": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_single_row"] is False
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_string_length(tmp_path):
    path = _minimal_slk()
    length = sylk_max_string_length(path)
    assert isinstance(length, int)
    assert length >= 5  # "Alpha" has 5 chars

    record = {"format": "sylk", "function": "sylk_max_string_length", "max_length": length}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_length"] >= 5
    assert json.dumps(loaded[0]) is not None


def test_find_value_returns_position(tmp_path):
    path = _minimal_slk()
    pos = find_value(path, "Alpha")
    assert pos is not None
    assert isinstance(pos, tuple)
    assert len(pos) == 2

    record = {"format": "sylk", "function": "find_value", "value": "Alpha", "found": True, "row": pos[0], "col": pos[1]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["found"] is True
    assert json.dumps(loaded[0]) is not None


def test_find_rows_by_value_returns_list(tmp_path):
    path = _minimal_slk()
    rows = find_rows_by_value(path, "Alpha")
    assert isinstance(rows, list)
    assert len(rows) >= 1

    record = {"format": "sylk", "function": "find_rows_by_value", "value": "Alpha", "row_count": len(rows)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 1
    assert json.dumps(loaded[0]) is not None
