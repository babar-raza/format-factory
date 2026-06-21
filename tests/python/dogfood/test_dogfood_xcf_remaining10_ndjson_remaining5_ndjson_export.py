"""
Dogfood pipeline: XCF remaining + NDJSON remaining -> NDJSON export.
Covers XCF: xcf_layer_count_squared, xcf_max_layer_area, xcf_total_canvas_pixels
Covers NDJSON: ndjson_avg_key_length, ndjson_avg_values_per_record, ndjson_boolean_ratio_total,
               ndjson_max_list_length, ndjson_null_ratio, ndjson_object_field_variance,
               ndjson_record_key_overlap, ndjson_total_value_count, ndjson_total_values_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_layer_count_squared, xcf_max_layer_area, xcf_total_canvas_pixels
from ndjson.ndjson_codec import (
    ndjson_avg_key_length,
    ndjson_avg_values_per_record,
    ndjson_boolean_ratio_total,
    ndjson_max_list_length,
    ndjson_null_ratio,
    ndjson_object_field_variance,
    ndjson_record_key_overlap,
    ndjson_total_value_count,
    ndjson_total_values_count,
    write_ndjson,
    load_ndjson,
)

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _ndjson_src(tmp_path):
    path = tmp_path / "src.ndjson"
    write_ndjson([
        {"a": 1, "b": True, "c": None, "d": [1, 2, 3]},
        {"a": 2, "b": False, "c": "text", "d": [4, 5]},
    ], str(path))
    return str(path)


# --- XCF ---

def test_xcf_layer_count_squared_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_layer_count_squared(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_layer_count_squared", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_max_layer_area_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_max_layer_area(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_max_layer_area", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_total_canvas_pixels_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_total_canvas_pixels(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "xcf", "function": "xcf_total_canvas_pixels", "pixels": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["pixels"] > 0
    assert json.dumps(loaded[0]) is not None


# --- NDJSON ---

def test_ndjson_avg_key_length_returns_float(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_avg_key_length(src)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_avg_key_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_avg_values_per_record_returns_float(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_avg_values_per_record(src)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_avg_values_per_record", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_boolean_ratio_total_returns_float(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_boolean_ratio_total(src)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_boolean_ratio_total", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_max_list_length_returns_int(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_max_list_length(src)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_max_list_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_null_ratio_returns_float(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_null_ratio(src)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_null_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_object_field_variance_returns_float(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_object_field_variance(src)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_object_field_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_record_key_overlap_returns_float(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_record_key_overlap(src)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_record_key_overlap", "overlap": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["overlap"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_total_value_count_returns_int(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_total_value_count(src)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_total_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_total_values_count_returns_int(tmp_path):
    src = _ndjson_src(tmp_path)
    result = ndjson_total_values_count(src)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_total_values_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
