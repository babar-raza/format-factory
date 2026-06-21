"""
Dogfood pipeline: ODS remaining + ODT remaining + TSV remaining + NDJSON remaining -> NDJSON export.
Covers ODS: ods_numeric_value_mean, ods_row_cell_sum, ods_total_sheet_count
Covers ODT: odt_lowercase_ratio, odt_max_paragraph_length, odt_nonempty_paragraph_count
Covers TSV: tsv_avg_field_length, tsv_file_size_bytes, tsv_is_single_row
Covers NDJSON: ndjson_max_field_count, ndjson_min_field_count, ndjson_null_field_count
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_numeric_value_mean, ods_row_cell_sum, ods_total_sheet_count
from odt.odt_parser import odt_lowercase_ratio, odt_max_paragraph_length, odt_nonempty_paragraph_count
from ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    ndjson_max_field_count,
    ndjson_min_field_count,
    ndjson_null_field_count,
)

sys.path.insert(0, str(_REPO))
from src.python.tsv.tsv_parser import tsv_avg_field_length, tsv_file_size_bytes, tsv_is_single_row

_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]
    return str(files[0])


# --- ODS ---

def test_ods_numeric_value_mean_returns_float(tmp_path):
    path = _ods_file()
    result = ods_numeric_value_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_numeric_value_mean", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_row_cell_sum_returns_int(tmp_path):
    path = _ods_file()
    result = ods_row_cell_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_row_cell_sum", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_total_sheet_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_total_sheet_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_total_sheet_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ODT ---

def test_odt_lowercase_ratio_returns_float(tmp_path):
    path = _odt_file()
    result = odt_lowercase_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "odt", "function": "odt_lowercase_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_odt_max_paragraph_length_returns_int(tmp_path):
    path = _odt_file()
    result = odt_max_paragraph_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_max_paragraph_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_nonempty_paragraph_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_nonempty_paragraph_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_nonempty_paragraph_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- TSV ---

def test_tsv_avg_field_length_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_avg_field_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_avg_field_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_file_size_bytes_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "tsv", "function": "tsv_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_is_single_row_returns_bool(tmp_path):
    path = _tsv_file()
    result = tsv_is_single_row(path)
    assert isinstance(result, bool)

    record = {"format": "tsv", "function": "tsv_is_single_row", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- NDJSON (create temp source file) ---

def test_ndjson_max_field_count_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1, "b": 2, "c": 3}, {"x": 10}], str(src))
    result = ndjson_max_field_count(str(src))
    assert isinstance(result, int)
    assert result == 3

    record = {"format": "ndjson", "function": "ndjson_max_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_min_field_count_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1, "b": 2, "c": 3}, {"x": 10}], str(src))
    result = ndjson_min_field_count(str(src))
    assert isinstance(result, int)
    assert result == 1

    record = {"format": "ndjson", "function": "ndjson_min_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 1
    assert json.dumps(loaded[0]) is not None


def test_ndjson_null_field_count_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": None, "b": 2}, {"a": None}, {"a": 5}], str(src))
    result = ndjson_null_field_count(str(src), "a")
    assert isinstance(result, int)
    assert result == 2

    record = {"format": "ndjson", "function": "ndjson_null_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 2
    assert json.dumps(loaded[0]) is not None
