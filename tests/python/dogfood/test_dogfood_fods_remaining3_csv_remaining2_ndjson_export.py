"""
Dogfood pipeline: FODS remaining analytics + CSV remaining analytics → NDJSON export.
Covers FODS: fods_avg_col_count, fods_is_single_cell, fods_row_count_variance,
             fods_avg_string_length, fods_col_count_variance, fods_cell_to_sheet_ratio
Covers CSV: csv_has_numeric_header, csv_nonempty_row_ratio, csv_numeric_sum,
            csv_is_single_row, csv_min_row_field_count, csv_is_multi_column
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fods.neutral_model import (
    fods_avg_col_count,
    fods_is_single_cell,
    fods_row_count_variance,
    fods_avg_string_length,
    fods_col_count_variance,
    fods_cell_to_sheet_ratio,
)
from fods.parser import parse_fods
from src.python.csv.csv_parser import (
    csv_has_numeric_header,
    csv_nonempty_row_ratio,
    csv_numeric_sum,
    csv_is_single_row,
    csv_min_row_field_count,
    csv_is_multi_column,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def _csv_file():
    # Skip invalid files
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_CSV_DIR.glob("*.csv")))))


def test_fods_avg_col_count_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_avg_col_count(model)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_avg_col_count", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_is_single_cell_returns_bool(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_is_single_cell(model)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_is_single_cell", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_row_count_variance_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_row_count_variance(model)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_row_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_string_length_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_avg_string_length(model)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_avg_string_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_col_count_variance_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_col_count_variance(model)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_col_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_cell_to_sheet_ratio_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_cell_to_sheet_ratio(model)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_cell_to_sheet_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_has_numeric_header_returns_bool(tmp_path):
    path = _csv_file()
    result = csv_has_numeric_header(path)
    assert isinstance(result, bool)

    record = {"format": "csv", "function": "csv_has_numeric_header", "has_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_nonempty_row_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_nonempty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_nonempty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_numeric_sum_returns_float(tmp_path):
    path = _csv_file()
    result = csv_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "csv", "function": "csv_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_csv_is_single_row_returns_bool(tmp_path):
    path = _csv_file()
    result = csv_is_single_row(path)
    assert isinstance(result, bool)

    record = {"format": "csv", "function": "csv_is_single_row", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_min_row_field_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_min_row_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_min_row_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_is_multi_column_returns_bool(tmp_path):
    path = _csv_file()
    result = csv_is_multi_column(path)
    assert isinstance(result, bool)

    record = {"format": "csv", "function": "csv_is_multi_column", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None
