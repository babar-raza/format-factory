"""
Dogfood pipeline: CSV remaining 2 + NDJSON remaining → NDJSON export.
Covers CSV: csv_header_count, csv_max_field_count, csv_is_multi_row, csv_column_count_variance
Covers NDJSON: ndjson_is_empty, ndjson_avg_string_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_header_count,
    csv_max_field_count,
    csv_is_multi_row,
    csv_column_count_variance,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson, ndjson_is_empty, ndjson_avg_string_length

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _minimal_csv():
    return str(_CSV_DIR / "minimal-2x2.csv")


def _make_ndjson(tmp_path):
    path = str(tmp_path / "sample.ndjson")
    write_ndjson([{"name": "Alice", "city": "NYC"}, {"name": "Bob", "country": "US"}], path)
    return path


def test_csv_header_count_returns_int(tmp_path):
    path = _minimal_csv()
    result = csv_header_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_header_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_max_field_count_returns_int(tmp_path):
    path = _minimal_csv()
    result = csv_max_field_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "csv", "function": "csv_max_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_csv_is_multi_row_returns_bool(tmp_path):
    path = _minimal_csv()
    result = csv_is_multi_row(path)
    assert isinstance(result, bool)
    assert result is True

    record = {"format": "csv", "function": "csv_is_multi_row", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_multi"] is True
    assert json.dumps(loaded[0]) is not None


def test_csv_column_count_variance_returns_float(tmp_path):
    path = _minimal_csv()
    result = csv_column_count_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "csv", "function": "csv_column_count_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_is_empty_returns_bool(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_is_empty(path)
    assert isinstance(result, bool)
    assert result is False

    record = {"format": "ndjson", "function": "ndjson_is_empty", "is_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_empty"] is False
    assert json.dumps(loaded[0]) is not None


def test_ndjson_avg_string_length_returns_float(tmp_path):
    path = _make_ndjson(tmp_path)
    result = ndjson_avg_string_length(path)
    assert isinstance(result, float)
    assert result >= 1.0

    record = {"format": "ndjson", "function": "ndjson_avg_string_length", "avg": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 1.0
    assert json.dumps(loaded[0]) is not None
