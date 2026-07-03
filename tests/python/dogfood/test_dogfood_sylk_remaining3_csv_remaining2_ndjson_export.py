"""
Dogfood pipeline: SYLK remaining analytics + CSV remaining analytics → NDJSON export.
Covers SYLK: get_row_values, sum_column, min_column_value, max_column_value,
             sylk_unique_value_count, find_rows_by_value
Covers CSV: get_capabilities, csv_row_count, csv_has_header,
            csv_numeric_density, csv_string_density, csv_data_density
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from sylk.sylk_analytics import sylk_unique_value_count
from sylk.sylk_parser import get_row_values, sum_column, min_column_value, max_column_value, find_rows_by_value, get_all_values
from src.python.csv.csv_parser import (
    get_capabilities as csv_get_capabilities,
    csv_row_count,
    csv_has_header,
    csv_numeric_density,
    csv_string_density,
    csv_data_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _csv_file():
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_CSV_DIR.glob("*.csv")))))


def test_sylk_get_row_values_returns_list(tmp_path):
    path = _sylk_file()
    result = get_row_values(path, 1)
    assert isinstance(result, list)

    record = {"format": "sylk", "function": "get_row_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_sum_column_returns_float(tmp_path):
    path = _sylk_file()
    result = sum_column(path, 0)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "sum_column", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_sylk_min_column_value_returns_value(tmp_path):
    path = _sylk_file()
    result = min_column_value(path, 0)
    # may be None if no numeric values

    record = {"format": "sylk", "function": "min_column_value", "value": str(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "value" in loaded[0]
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_column_value_returns_value(tmp_path):
    path = _sylk_file()
    result = max_column_value(path, 0)
    # may be None if no numeric values

    record = {"format": "sylk", "function": "max_column_value", "value": str(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "value" in loaded[0]
    assert json.dumps(loaded[0]) is not None


def test_sylk_unique_value_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_unique_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_unique_value_count", "unique_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["unique_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_find_rows_by_value_returns_list(tmp_path):
    path = _sylk_file()
    all_vals = get_all_values(path)
    str_val = next((v for v in all_vals if isinstance(v, str)), None)
    if str_val is None:
        pytest.skip("No string values in SYLK file")
    result = find_rows_by_value(path, str_val)
    assert isinstance(result, list)

    record = {"format": "sylk", "function": "find_rows_by_value", "row_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_get_capabilities_returns_dict(tmp_path):
    result = csv_get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result
    assert result["format"] == "csv"

    record = {"format": "csv", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "csv"
    assert json.dumps(loaded[0]) is not None


def test_csv_row_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_row_count", "row_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_has_header_returns_bool(tmp_path):
    path = _csv_file()
    result = csv_has_header(path)
    assert isinstance(result, bool)

    record = {"format": "csv", "function": "csv_has_header", "has_header": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_header"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_numeric_density_returns_float(tmp_path):
    path = _csv_file()
    result = csv_numeric_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_numeric_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_string_density_returns_float(tmp_path):
    path = _csv_file()
    result = csv_string_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_string_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_data_density_returns_float(tmp_path):
    path = _csv_file()
    result = csv_data_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_data_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None
