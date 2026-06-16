"""
Dogfood pipeline: Gnumeric remaining 2 → NDJSON export.
Covers: get_all_values, get_cell_count, get_cell_value, extract_values,
        fill_column, fill_row
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import get_all_values, get_cell_count, get_cell_value, extract_values, fill_column, fill_row, load
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _gnumeric_path():
    for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
        if "minimal" in f.name:
            return str(f)
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def test_gnumeric_get_all_values_returns_list(tmp_path):
    path = _gnumeric_path()
    model = load(path)
    result = get_all_values(model, 0)
    assert isinstance(result, list)
    record = {"format": "gnumeric", "function": "get_all_values", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_cell_count_returns_int(tmp_path):
    path = _gnumeric_path()
    result = get_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "gnumeric", "function": "get_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_cell_value_returns_str(tmp_path):
    path = _gnumeric_path()
    model = load(path)
    result = get_cell_value(model, 0, 0, 0)
    assert isinstance(result, str)
    record = {"format": "gnumeric", "function": "get_cell_value", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], str)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_extract_values_returns_list(tmp_path):
    path = _gnumeric_path()
    result = extract_values(path)
    assert isinstance(result, list)
    record = {"format": "gnumeric", "function": "extract_values", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_fill_column_returns_dict(tmp_path):
    path = _gnumeric_path()
    model = load(path)
    result = fill_column(model, 0, 0, ["a", "b"])
    assert isinstance(result, dict)
    assert len(result.get("sheets", [])) >= 1
    record = {"format": "gnumeric", "function": "fill_column", "sheet_count": len(result.get("sheets", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_fill_row_returns_dict(tmp_path):
    path = _gnumeric_path()
    model = load(path)
    result = fill_row(model, 0, 0, ["x", "y"])
    assert isinstance(result, dict)
    assert len(result.get("sheets", [])) >= 1
    record = {"format": "gnumeric", "function": "fill_row", "sheet_count": len(result.get("sheets", []))}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None
