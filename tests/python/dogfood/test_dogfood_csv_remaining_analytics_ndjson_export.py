"""
Dogfood pipeline: CSV remaining analytics → NDJSON export.
Covers: probe_csv, csv_is_empty, csv_row_length_variance, csv_column_type_counts,
        csv_column_name_lengths, parse_csv_strict
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    parse_csv_strict,
    probe_csv,
    csv_column_type_counts,
    csv_row_length_variance,
    csv_is_empty,
    csv_column_name_lengths,
)
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"


def _minimal_csv():
    return str(_CSV_DIR / "minimal-2x2.csv")


def test_probe_csv_returns_dict(tmp_path):
    path = _minimal_csv()
    result = probe_csv(path)
    assert isinstance(result, dict)
    assert result.get("exists") is True
    assert result.get("delimiter") == ","

    record = {"format": "csv", "function": "probe_csv", "delimiter": result.get("delimiter")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["delimiter"] == ","
    assert json.dumps(loaded[0]) is not None


def test_csv_is_empty_returns_bool(tmp_path):
    path = _minimal_csv()
    result = csv_is_empty(path)
    assert isinstance(result, bool)
    assert result is False

    record = {"format": "csv", "function": "csv_is_empty", "is_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_empty"] is False
    assert json.dumps(loaded[0]) is not None


def test_csv_row_length_variance_returns_float(tmp_path):
    path = _minimal_csv()
    result = csv_row_length_variance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "csv", "function": "csv_row_length_variance", "variance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_csv_column_type_counts_returns_dict(tmp_path):
    path = _minimal_csv()
    result = csv_column_type_counts(path)
    assert isinstance(result, dict)
    assert len(result) > 0

    record = {"format": "csv", "function": "csv_column_type_counts",
              "numeric": result.get("numeric", 0), "string": result.get("string", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["numeric"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_column_name_lengths_returns_list(tmp_path):
    path = _minimal_csv()
    result = csv_column_name_lengths(path)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(isinstance(x, int) for x in result)

    record = {"format": "csv", "function": "csv_column_name_lengths", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_parse_csv_strict_returns_dict(tmp_path):
    path = _minimal_csv()
    result = parse_csv_strict(path)
    assert isinstance(result, dict)
    assert "headers" in result

    record = {"format": "csv", "function": "parse_csv_strict",
              "row_count": result.get("row_count", 0), "column_count": result.get("column_count", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["column_count"] >= 1
    assert json.dumps(loaded[0]) is not None
