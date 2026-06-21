"""
Dogfood pipeline: ABW remaining + CSV remaining + SYLK remaining + ODS remaining + PBM remaining -> NDJSON export.
Covers ABW: abw_alpha_char_count, abw_space_count
Covers CSV: csv_blank_field_ratio, csv_numeric_field_ratio, csv_row_length_range, csv_value_sum
Covers SYLK: sylk_nonempty_row_count, sylk_string_ratio
Covers ODS: ods_cell_text_density, ods_has_numeric_content, ods_sheet_cell_variance
Covers PBM: pbm_black_white_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from abw.abw_codec import abw_alpha_char_count, abw_space_count
from src.python.csv.csv_parser import (
    csv_blank_field_ratio,
    csv_numeric_field_ratio,
    csv_row_length_range,
    csv_value_sum,
)
from sylk.sylk_parser import sylk_nonempty_row_count, sylk_string_ratio
from ods.ods_parser import ods_cell_text_density, ods_has_numeric_content, ods_sheet_cell_variance
from pbm.pbm_parser import pbm_black_white_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _csv_file():
    files = [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]
    return str(files[0])


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


# --- ABW ---

def test_abw_alpha_char_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_alpha_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_alpha_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_space_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_space_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_space_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- CSV ---

def test_csv_blank_field_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_blank_field_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_blank_field_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_numeric_field_ratio_returns_float(tmp_path):
    path = _csv_file()
    result = csv_numeric_field_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_numeric_field_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_row_length_range_returns_int(tmp_path):
    path = _csv_file()
    result = csv_row_length_range(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "csv", "function": "csv_row_length_range", "range": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_value_sum_returns_number(tmp_path):
    path = _csv_file()
    result = csv_value_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "csv", "function": "csv_value_sum", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


# --- SYLK ---

def test_sylk_nonempty_row_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_nonempty_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_nonempty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_string_ratio_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_string_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "sylk", "function": "sylk_string_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- ODS ---

def test_ods_cell_text_density_returns_float(tmp_path):
    path = _ods_file()
    result = ods_cell_text_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_cell_text_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_has_numeric_content_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_numeric_content(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_numeric_content", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_sheet_cell_variance_returns_float(tmp_path):
    path = _ods_file()
    result = ods_sheet_cell_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_sheet_cell_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- PBM ---

def test_pbm_black_white_ratio_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_black_white_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_black_white_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None
