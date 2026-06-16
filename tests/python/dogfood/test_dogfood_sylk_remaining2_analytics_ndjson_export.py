"""
Dogfood pipeline: SYLK remaining analytics → NDJSON export.
Covers: get_capabilities, get_cell_count, get_cell_value, get_column_count,
        get_row_count, count_distinct_values
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    get_capabilities,
    get_cell_count,
    get_cell_value,
    get_column_count,
    get_row_count,
    count_distinct_values,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def test_sylk_get_capabilities_returns_dict(tmp_path):
    result = get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result

    record = {"format": "sylk", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "sylk"
    assert json.dumps(loaded[0]) is not None


def test_sylk_get_cell_count_returns_int(tmp_path):
    path = _sylk_file()
    result = get_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "get_cell_count", "cell_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_get_cell_value_returns_value(tmp_path):
    path = _sylk_file()
    result = get_cell_value(path, 1, 1)
    # result may be None or a value

    record = {"format": "sylk", "function": "get_cell_value", "value": str(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "value" in loaded[0]
    assert json.dumps(loaded[0]) is not None


def test_sylk_get_column_count_returns_int(tmp_path):
    path = _sylk_file()
    result = get_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "get_column_count", "col_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["col_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_get_row_count_returns_int(tmp_path):
    path = _sylk_file()
    result = get_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "get_row_count", "row_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_count_distinct_values_returns_int(tmp_path):
    path = _sylk_file()
    result = count_distinct_values(path, 0)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "count_distinct_values", "distinct_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["distinct_count"] >= 0
    assert json.dumps(loaded[0]) is not None
