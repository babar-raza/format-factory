"""
Dogfood pipeline: CSV remaining + TSV remaining -> NDJSON export.
Covers CSV: csv_alpha_field_count, csv_distinct_col_count, csv_distinct_value_count,
            csv_duplicate_row_count, csv_empty_cell_count, csv_empty_cell_ratio
Covers TSV: tsv_alpha_field_count, tsv_average_cell_length, tsv_avg_field_text_length,
            tsv_avg_fields_per_row, tsv_cell_to_row_ratio, tsv_column_count_per_row
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
    csv_alpha_field_count,
    csv_distinct_col_count,
    csv_distinct_value_count,
    csv_duplicate_row_count,
    csv_empty_cell_count,
    csv_empty_cell_ratio,
)
from src.python.tsv.tsv_parser import (
    tsv_alpha_field_count,
    tsv_average_cell_length,
    tsv_avg_field_text_length,
    tsv_avg_fields_per_row,
    tsv_cell_to_row_ratio,
    tsv_column_count_per_row,
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

def test_csv_alpha_field_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_alpha_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_alpha_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_distinct_col_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_distinct_col_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_distinct_col_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_distinct_value_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_distinct_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_distinct_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_duplicate_row_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_duplicate_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_duplicate_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_empty_cell_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_empty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_empty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_empty_cell_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_empty_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_empty_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- TSV ---

def test_tsv_alpha_field_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_alpha_field_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_alpha_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_average_cell_length_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_average_cell_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_average_cell_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_avg_field_text_length_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_avg_field_text_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_avg_field_text_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_avg_fields_per_row_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_avg_fields_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_avg_fields_per_row", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_cell_to_row_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_cell_to_row_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_cell_to_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_column_count_per_row_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_column_count_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_column_count_per_row", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None
