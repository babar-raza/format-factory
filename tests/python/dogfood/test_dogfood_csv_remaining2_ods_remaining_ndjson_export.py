"""
Dogfood pipeline: CSV remaining 2 + ODS remaining → NDJSON export.
Covers: csv_column_count, csv_all_rows_same_length, csv_average_field_length, csv_avg_row_length,
        count_sheets (ods), count_nonempty_cells (ods)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.ff_csv.csv_parser import csv_column_count, csv_all_rows_same_length, csv_average_field_length, csv_avg_row_length
from ods.ods_parser import count_sheets, count_nonempty_cells
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _csv_file():
    for f in sorted(_CSV_DIR.glob("*.csv")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_CSV_DIR.glob("*.csv")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_csv_column_count_returns_int(tmp_path):
    path = _csv_file()
    result = csv_column_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "csv", "function": "csv_column_count", "column_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["column_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_csv_all_rows_same_length_returns_bool(tmp_path):
    path = _csv_file()
    result = csv_all_rows_same_length(path)
    assert isinstance(result, bool)

    record = {"format": "csv", "function": "csv_all_rows_same_length", "uniform": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["uniform"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_average_field_length_returns_float(tmp_path):
    path = _csv_file()
    result = csv_average_field_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "csv", "function": "csv_average_field_length", "avg_length": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_length"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_csv_avg_row_length_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_row_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "csv", "function": "csv_avg_row_length", "avg_row_length": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_row_length"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_count_sheets_returns_int(tmp_path):
    path = _ods_file()
    result = count_sheets(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "ods", "function": "count_sheets", "sheet_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sheet_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_ods_count_nonempty_cells_returns_int(tmp_path):
    path = _ods_file()
    result = count_nonempty_cells(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "count_nonempty_cells", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
