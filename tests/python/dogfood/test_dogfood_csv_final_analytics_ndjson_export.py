"""
Dogfood pipeline: CSV final analytics → NDJSON export.
Covers: csv_is_single_column, csv_is_all_numeric, csv_max_field_value_length,
        csv_unique_value_count + ODS ods_all_sheets_have_data, ods_is_single_sheet
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_is_single_column,
    csv_is_all_numeric,
    csv_max_field_value_length,
    csv_unique_value_count,
)
from src.python.ods.ods_parser import ods_all_sheets_have_data, ods_is_single_sheet
from src.python.ndjson.ndjson_codec import write_ndjson, load_ndjson

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _valid_csv_files():
    return sorted(f for f in _CSV_DIR.glob("*.csv") if "invalid" not in f.name)


def _valid_ods_files():
    return sorted(_ODS_DIR.glob("*.ods"))


def test_csv_is_single_column(tmp_path):
    path = str(_valid_csv_files()[0])
    result = csv_is_single_column(path)
    assert isinstance(result, bool)

    record = {"format": "csv", "function": "csv_is_single_column", "is_single_column": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single_column"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_is_all_numeric(tmp_path):
    path = str(_valid_csv_files()[0])
    result = csv_is_all_numeric(path)
    assert isinstance(result, bool)
    assert result is False  # multi-column.csv has text fields

    record = {"format": "csv", "function": "csv_is_all_numeric", "is_all_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_all_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_csv_max_field_value_length(tmp_path):
    path = str(_valid_csv_files()[0])
    length = csv_max_field_value_length(path)
    assert isinstance(length, int)
    assert length >= 0

    record = {"format": "csv", "function": "csv_max_field_value_length", "max_length": length}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_unique_value_count(tmp_path):
    path = str(_valid_csv_files()[0])
    count = csv_unique_value_count(path)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "csv", "function": "csv_unique_value_count", "unique_count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["unique_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_all_sheets_have_data(tmp_path):
    path = str(_valid_ods_files()[0])
    result = ods_all_sheets_have_data(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_all_sheets_have_data", "all_have_data": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_have_data"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_is_single_sheet(tmp_path):
    path = str(_valid_ods_files()[0])
    result = ods_is_single_sheet(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_single_sheet", "is_single_sheet": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single_sheet"], bool)
    assert json.dumps(loaded[0]) is not None
