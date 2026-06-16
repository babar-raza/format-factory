"""
Dogfood pipeline: SYLK remaining analytics + NDJSON remaining analytics → NDJSON export.
Covers: count_nonempty_cells, find_value, get_all_values, average_column (sylk),
        count_records, count_unique_values (ndjson)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import count_nonempty_cells, find_value, get_all_values, average_column
from ndjson.ndjson_codec import count_records, count_unique_values, write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def test_sylk_count_nonempty_cells_returns_int(tmp_path):
    path = _sylk_file()
    result = count_nonempty_cells(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "count_nonempty_cells", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_find_value_returns_tuple(tmp_path):
    path = _sylk_file()
    all_vals = get_all_values(path)
    # Find a string value
    str_val = next((v for v in all_vals if isinstance(v, str)), None)
    if str_val is None:
        pytest.skip("No string values in SYLK file")
    result = find_value(path, str_val)
    assert isinstance(result, tuple)
    assert len(result) == 2

    record = {"format": "sylk", "function": "find_value", "row": result[0], "col": result[1]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_get_all_values_returns_list(tmp_path):
    path = _sylk_file()
    result = get_all_values(path)
    assert isinstance(result, list)
    assert len(result) >= 1

    record = {"format": "sylk", "function": "get_all_values", "value_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_sylk_average_column_returns_float(tmp_path):
    path = _sylk_file()
    result = average_column(path, 0)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "average_column", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ndjson_count_records_returns_int(tmp_path):
    # Write records then count them
    records = [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}, {"x": 3, "y": "a"}]
    ndjson_out = tmp_path / "data.ndjson"
    write_ndjson(records, str(ndjson_out))
    result = count_records(str(ndjson_out))
    assert isinstance(result, int)
    assert result == 3

    summary = {"format": "ndjson", "function": "count_records", "count": result}
    out2 = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out2))
    loaded = load_ndjson(str(out2))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_count_unique_values_returns_int(tmp_path):
    # Write records then count unique values for a field
    records = [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}, {"x": 1, "y": "a"}]
    ndjson_out = tmp_path / "data.ndjson"
    write_ndjson(records, str(ndjson_out))
    result = count_unique_values(str(ndjson_out), "y")
    assert isinstance(result, int)
    assert result == 2

    summary = {"format": "ndjson", "function": "count_unique_values", "unique_count": result}
    out2 = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out2))
    loaded = load_ndjson(str(out2))
    assert loaded[0]["unique_count"] == 2
    assert json.dumps(loaded[0]) is not None
