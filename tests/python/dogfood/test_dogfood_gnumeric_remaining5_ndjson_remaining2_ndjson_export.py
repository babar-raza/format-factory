"""
Dogfood pipeline: Gnumeric remaining analytics + NDJSON remaining analytics → NDJSON export.
Covers Gnumeric: gnumeric_has_empty_cells, gnumeric_total_row_count, gnumeric_row_count_variance,
                 gnumeric_sheet_name_lengths, gnumeric_max_cell_value_length, gnumeric_is_multi_sheet
Covers NDJSON: ndjson_list_field_count, ndjson_field_count_variance, ndjson_max_nesting_depth,
               ndjson_avg_numeric_value, ndjson_total_string_length, ndjson_numeric_density
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_has_empty_cells,
    gnumeric_total_row_count,
    gnumeric_row_count_variance,
    gnumeric_sheet_name_lengths,
    gnumeric_max_cell_value_length,
    gnumeric_is_multi_sheet,
)
from ndjson.ndjson_codec import (
    ndjson_list_field_count,
    ndjson_field_count_variance,
    ndjson_max_nesting_depth,
    ndjson_avg_numeric_value,
    ndjson_total_string_length,
    ndjson_numeric_density,
    write_ndjson,
    load_ndjson,
)

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _make_ndjson(tmp_path):
    """Create a test NDJSON file with numeric and string fields."""
    records = [
        {"x": 1, "name": "alpha", "tags": ["a", "b"]},
        {"x": 2, "name": "beta", "tags": ["c"]},
        {"x": 3, "name": "gamma", "tags": ["d", "e", "f"]},
    ]
    out = tmp_path / "test_input.ndjson"
    write_ndjson(records, str(out))
    return str(out)


def test_gnumeric_has_empty_cells_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_has_empty_cells(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_has_empty_cells", "has_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_empty"], bool)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_total_row_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_total_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_total_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_row_count_variance_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_row_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_row_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_sheet_name_lengths_returns_list(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_sheet_name_lengths(path)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(v, int) for v in result)

    record = {"format": "gnumeric", "function": "gnumeric_sheet_name_lengths", "lengths": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["lengths"], list)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_max_cell_value_length_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_max_cell_value_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_max_cell_value_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_is_multi_sheet_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_is_multi_sheet(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_is_multi_sheet", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ndjson_list_field_count_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_list_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_list_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_field_count_variance_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_field_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_field_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_max_nesting_depth_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_max_nesting_depth(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_max_nesting_depth", "depth": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["depth"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_avg_numeric_value_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_avg_numeric_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "ndjson", "function": "ndjson_avg_numeric_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ndjson_total_string_length_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_total_string_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_total_string_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_numeric_density_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_numeric_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_numeric_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None
