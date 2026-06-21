"""
Dogfood pipeline: NDJSON remaining analytics + CSV remaining analytics → NDJSON export.
Covers NDJSON: ndjson_min_record_size, ndjson_has_numeric_fields, ndjson_has_lists,
               ndjson_schema_consistency, ndjson_total_numeric_sum, ndjson_is_single_record,
               ndjson_boolean_density, ndjson_max_field_value_length
Covers CSV: csv_nonempty_cell_ratio, csv_numeric_cell_ratio, csv_field_count_variance,
            csv_longest_field_value
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from ndjson.ndjson_codec import (
    ndjson_min_record_size,
    ndjson_has_numeric_fields,
    ndjson_has_lists,
    ndjson_schema_consistency,
    ndjson_total_numeric_sum,
    ndjson_is_single_record,
    ndjson_boolean_density,
    ndjson_max_field_value_length,
    write_ndjson,
    load_ndjson,
)
from src.python.csv.csv_parser import (
    csv_nonempty_cell_ratio,
    csv_numeric_cell_ratio,
    csv_field_count_variance,
    csv_longest_field_value,
)

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _csv_file():
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_CSV_DIR.glob("*.csv")))))


def _make_ndjson(tmp_path):
    records = [
        {"x": 1, "name": "alpha", "tags": ["a", "b"], "active": True},
        {"x": 2, "name": "beta", "tags": ["c"], "active": False},
        {"x": 3, "name": "gamma", "tags": ["d", "e"], "active": True},
    ]
    out = tmp_path / "test_input.ndjson"
    write_ndjson(records, str(out))
    return str(out)


def test_ndjson_min_record_size_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_min_record_size(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_min_record_size", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_has_numeric_fields_returns_bool(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_has_numeric_fields(path)
    assert isinstance(result, bool)

    record = {"format": "ndjson", "function": "ndjson_has_numeric_fields", "has_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ndjson_has_lists_returns_bool(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_has_lists(path)
    assert isinstance(result, bool)

    record = {"format": "ndjson", "function": "ndjson_has_lists", "has_lists": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_lists"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ndjson_schema_consistency_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_schema_consistency(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_schema_consistency", "consistency": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["consistency"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_total_numeric_sum_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_total_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "ndjson", "function": "ndjson_total_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ndjson_is_single_record_returns_bool(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_is_single_record(path)
    assert isinstance(result, bool)

    record = {"format": "ndjson", "function": "ndjson_is_single_record", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ndjson_boolean_density_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_boolean_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ndjson", "function": "ndjson_boolean_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_max_field_value_length_returns_int(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_max_field_value_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_max_field_value_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_nonempty_cell_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_nonempty_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_nonempty_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_numeric_cell_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_numeric_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_numeric_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_field_count_variance_returns_float(tmp_path):
    path = _csv_file()
    result = csv_field_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_field_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_longest_field_value_returns_int(tmp_path):
    path = _csv_file()
    result = csv_longest_field_value(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_longest_field_value", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None
