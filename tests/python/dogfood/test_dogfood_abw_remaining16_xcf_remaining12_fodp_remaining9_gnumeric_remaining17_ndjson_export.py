"""
Dogfood pipeline: ABW remaining + XCF remaining + FODP remaining + Gnumeric remaining -> NDJSON export.
Covers ABW: abw_consonant_count, abw_digit_count, abw_distinct_word_ratio
Covers XCF: xcf_color_mode_name, xcf_diagonal, xcf_dimension_sum
Covers FODP: fodp_avg_title_words, fodp_digit_count, fodp_empty_slide_count
Covers Gnumeric: gnumeric_average_cells_per_sheet, gnumeric_avg_string_cells_per_sheet, gnumeric_cell_value_total_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_consonant_count, abw_digit_count, abw_distinct_word_ratio
from xcf.xcf_parser import xcf_color_mode_name, xcf_diagonal, xcf_dimension_sum
from fodp.fodp_codec import fodp_avg_title_words, fodp_digit_count, fodp_empty_slide_count
from gnumeric.gnumeric_codec import (
    gnumeric_average_cells_per_sheet,
    gnumeric_avg_string_cells_per_sheet,
    gnumeric_cell_value_total_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


# --- ABW ---

def test_abw_consonant_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_consonant_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_consonant_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_digit_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_digit_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_digit_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_distinct_word_ratio_returns_float(tmp_path):
    path = _abw_file()
    result = abw_distinct_word_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "abw", "function": "abw_distinct_word_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- XCF ---

def test_xcf_color_mode_name_returns_str(tmp_path):
    path = _xcf_file()
    result = xcf_color_mode_name(path)
    assert isinstance(result, str)
    assert len(result) > 0

    record = {"format": "xcf", "function": "xcf_color_mode_name", "mode": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["mode"], str)
    assert json.dumps(loaded[0]) is not None


def test_xcf_diagonal_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_diagonal(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_diagonal", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_dimension_sum_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_dimension_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_dimension_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODP ---

def test_fodp_avg_title_words_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_title_words(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_avg_title_words", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_digit_count_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_digit_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_digit_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_empty_slide_count_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_empty_slide_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_empty_slide_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- Gnumeric ---

def test_gnumeric_average_cells_per_sheet_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_average_cells_per_sheet(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_average_cells_per_sheet", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_string_cells_per_sheet_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_avg_string_cells_per_sheet(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_avg_string_cells_per_sheet", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_cell_value_total_length_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cell_value_total_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cell_value_total_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None
