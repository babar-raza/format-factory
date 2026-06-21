"""
Dogfood pipeline: FODG remaining + ODS remaining + CSV remaining + XCF remaining -> NDJSON export.
Covers FODG: fodg_avg_text_item_length, fodg_file_size_bytes, fodg_min_text_item_length,
             fodg_text_item_count, fodg_unique_text_item_count
Covers ODS: ods_avg_cell_text_length, ods_has_single_sheet, ods_sheets_with_data
Covers CSV: csv_header_uniqueness_ratio, csv_longest_field_length
Covers XCF: xcf_aspect_ratio_string, xcf_has_single_layer
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from fodg.fodg_codec import (
    fodg_avg_text_item_length,
    fodg_file_size_bytes,
    fodg_min_text_item_length,
    fodg_text_item_count,
    fodg_unique_text_item_count,
)
from ods.ods_parser import ods_avg_cell_text_length, ods_has_single_sheet, ods_sheets_with_data
from src.python.csv.csv_parser import csv_header_uniqueness_ratio, csv_longest_field_length
from xcf.xcf_parser import xcf_aspect_ratio_string, xcf_has_single_layer
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _fodg_file():
    return str(next(iter(sorted(_FODG_DIR.glob("*.fodg")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _csv_file():
    files = [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]
    return str(files[0])


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_fodg_avg_text_item_length_returns_float(tmp_path):
    path = _fodg_file()
    result = fodg_avg_text_item_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_avg_text_item_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_file_size_bytes_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_file_size_bytes(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_min_text_item_length_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_min_text_item_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_min_text_item_length", "min_len": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["min_len"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_text_item_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_text_item_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_text_item_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_unique_text_item_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_unique_text_item_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_unique_text_item_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_cell_text_length_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_cell_text_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_avg_cell_text_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_has_single_sheet_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_single_sheet(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_single_sheet", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_sheets_with_data_returns_int(tmp_path):
    path = _ods_file()
    result = ods_sheets_with_data(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_sheets_with_data", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_header_uniqueness_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_header_uniqueness_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_header_uniqueness_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_longest_field_length_returns_int(tmp_path):
    path = _csv_file()
    result = csv_longest_field_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_longest_field_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_aspect_ratio_string_returns_str(tmp_path):
    path = _xcf_file()
    result = xcf_aspect_ratio_string(path)
    assert isinstance(result, str)
    assert len(result) > 0

    record = {"format": "xcf", "function": "xcf_aspect_ratio_string", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], str)
    assert json.dumps(loaded[0]) is not None


def test_xcf_has_single_layer_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_has_single_layer(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_has_single_layer", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None
