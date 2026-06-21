"""
Dogfood pipeline: FODS remaining + ODS remaining -> NDJSON export.
Covers FODS: fods_empty_cell_ratio, fods_max_row_count, fods_min_cell_count_per_row,
             fods_nonempty_cell_count_all, fods_sheet_count, fods_total_row_count
Covers ODS: ods_avg_row_length, ods_avg_value_text_length, ods_cell_count_per_sheet,
            ods_cells_to_rows_ratio, ods_file_size_bytes, ods_rows_to_sheets_ratio
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods
from fods.neutral_model import (
    fods_empty_cell_ratio,
    fods_max_row_count,
    fods_min_cell_count_per_row,
    fods_nonempty_cell_count_all,
    fods_sheet_count,
    fods_total_row_count,
)
from ods.ods_parser import (
    ods_avg_row_length,
    ods_avg_value_text_length,
    ods_cell_count_per_sheet,
    ods_cells_to_rows_ratio,
    ods_file_size_bytes,
    ods_rows_to_sheets_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


# --- FODS ---

def test_fods_empty_cell_ratio_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_empty_cell_ratio(workbook)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_empty_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fods_max_row_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_max_row_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_max_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_min_cell_count_per_row_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_min_cell_count_per_row(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_min_cell_count_per_row", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_nonempty_cell_count_all_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_nonempty_cell_count_all(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_nonempty_cell_count_all", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_sheet_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_sheet_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_sheet_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_total_row_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_total_row_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_total_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ODS ---

def test_ods_avg_row_length_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_row_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_avg_row_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_value_text_length_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_value_text_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_avg_value_text_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_cell_count_per_sheet_returns_float(tmp_path):
    path = _ods_file()
    result = ods_cell_count_per_sheet(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_cell_count_per_sheet", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_cells_to_rows_ratio_returns_float(tmp_path):
    path = _ods_file()
    result = ods_cells_to_rows_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_cells_to_rows_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_file_size_bytes_returns_int(tmp_path):
    path = _ods_file()
    result = ods_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "ods", "function": "ods_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None


def test_ods_rows_to_sheets_ratio_returns_float(tmp_path):
    path = _ods_file()
    result = ods_rows_to_sheets_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_rows_to_sheets_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None
