"""
Dogfood pipeline: Gnumeric remaining analytics + NDJSON remaining analytics → NDJSON export.
Covers Gnumeric: gnumeric_avg_numeric_value, gnumeric_nonempty_row_ratio, gnumeric_longest_row_index,
                 gnumeric_numeric_sum_all, gnumeric_empty_column_count, gnumeric_cell_count_variance
Covers NDJSON: ndjson_string_density, ndjson_avg_list_length, ndjson_nested_count,
               ndjson_min_record_fields, ndjson_total_keys, ndjson_deepest_nesting
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_avg_numeric_value,
    gnumeric_nonempty_row_ratio,
    gnumeric_longest_row_index,
    gnumeric_numeric_sum_all,
    gnumeric_empty_column_count,
    gnumeric_cell_count_variance,
)
from ndjson.ndjson_codec import (
    ndjson_string_density,
    ndjson_avg_list_length,
    ndjson_nested_count,
    ndjson_min_record_fields,
    ndjson_total_keys,
    ndjson_deepest_nesting,
    write_ndjson,
    load_ndjson,
)

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _gnumeric_file():
    files = sorted(_GNUMERIC_DIR.glob("*.gnumeric"))
    # prefer minimal-spreadsheet which has cells
    for f in files:
        if "minimal-spreadsheet" in f.name:
            return str(f)
    return str(files[0])


def _make_ndjson(tmp_path):
    records = [
        {"x": 1, "name": "alpha", "tags": ["a", "b"], "nested": {"k": 1}},
        {"x": 2, "name": "beta", "tags": ["c"], "nested": {"k": 2}},
    ]
    out = tmp_path / "test_input.ndjson"
    write_ndjson(records, str(out))
    return str(out)


def test_gnumeric_avg_numeric_value_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_avg_numeric_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "gnumeric_avg_numeric_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_nonempty_row_ratio_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_nonempty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "gnumeric", "function": "gnumeric_nonempty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_longest_row_index_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_longest_row_index(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_longest_row_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_numeric_sum_all_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_numeric_sum_all(path)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "gnumeric_numeric_sum_all", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_empty_column_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_empty_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_empty_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_cell_count_variance_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cell_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cell_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_string_density_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_string_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_string_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_avg_list_length_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_avg_list_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_avg_list_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_nested_count_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_nested_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_nested_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_min_record_fields_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_min_record_fields(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_min_record_fields", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_total_keys_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_total_keys(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_total_keys", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_deepest_nesting_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_deepest_nesting(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_deepest_nesting", "depth": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["depth"] >= 0
    assert json.dumps(loaded[0]) is not None
