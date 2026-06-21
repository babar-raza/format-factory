"""
Dogfood pipeline: CSV remaining + TSV remaining -> NDJSON export.
Covers CSV: csv_empty_column_count, csv_empty_field_count, csv_empty_row_ratio,
            csv_field_length_variance, csv_field_type_ratio, csv_file_size_bytes
Covers TSV: tsv_all_rows_same_length, tsv_column_type_ratio, tsv_column_value_variance,
            tsv_data_completeness, tsv_distinct_value_ratio, tsv_duplicate_row_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_empty_column_count,
    csv_empty_field_count,
    csv_empty_row_ratio,
    csv_field_length_variance,
    csv_field_type_ratio,
    csv_file_size_bytes,
)
from src.python.tsv.tsv_parser import (
    tsv_all_rows_same_length,
    tsv_column_type_ratio,
    tsv_column_value_variance,
    tsv_data_completeness,
    tsv_distinct_value_ratio,
    tsv_duplicate_row_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _csv_file():
    files = [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]
    return str(files[0])


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]
    return str(files[0])


# --- CSV ---

def test_csv_empty_column_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_empty_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_empty_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_empty_field_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_empty_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_empty_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_empty_row_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_empty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_empty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_field_length_variance_returns_float(tmp_path):
    path = _csv_file()
    result = csv_field_length_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_field_length_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_field_type_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_field_type_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_field_type_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_file_size_bytes_returns_int(tmp_path):
    path = _csv_file()
    result = csv_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "csv", "function": "csv_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None


# --- TSV ---

def test_tsv_all_rows_same_length_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_all_rows_same_length(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_all_rows_same_length", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_tsv_column_type_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_column_type_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_column_type_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_column_value_variance_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_column_value_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_column_value_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_data_completeness_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_data_completeness(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_data_completeness", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["value"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_distinct_value_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_distinct_value_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_distinct_value_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_duplicate_row_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_duplicate_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_duplicate_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
