"""
Dogfood pipeline: ABW remaining + XCF remaining + FODP remaining + Gnumeric remaining -> NDJSON export.
Covers ABW: abw_avg_sentence_word_count, abw_avg_words_per_paragraph, abw_capital_word_count
Covers XCF: xcf_aspect_ratio, xcf_bytes_per_pixel, xcf_canvas_aspect_ratio
Covers FODP: fodp_avg_sentence_length, fodp_avg_shape_text_length, fodp_avg_text_length
Covers Gnumeric: gnumeric_all_sheets_have_data, gnumeric_avg_string_length, gnumeric_cell_count_all_sheets
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_avg_sentence_word_count, abw_avg_words_per_paragraph, abw_capital_word_count
from xcf.xcf_parser import xcf_aspect_ratio, xcf_bytes_per_pixel, xcf_canvas_aspect_ratio
from fodp.fodp_codec import fodp_avg_sentence_length, fodp_avg_shape_text_length, fodp_avg_text_length
from gnumeric.gnumeric_codec import (
    gnumeric_all_sheets_have_data,
    gnumeric_avg_string_length,
    gnumeric_cell_count_all_sheets,
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

def test_abw_avg_sentence_word_count_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_sentence_word_count(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_sentence_word_count", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_words_per_paragraph_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_words_per_paragraph(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_words_per_paragraph", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_capital_word_count_returns_int(tmp_path):
    path = _abw_file()
    result = abw_capital_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_capital_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- XCF ---

def test_xcf_aspect_ratio_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_aspect_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_aspect_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_bytes_per_pixel_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_bytes_per_pixel(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_bytes_per_pixel", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_canvas_aspect_ratio_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_canvas_aspect_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_canvas_aspect_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODP ---

def test_fodp_avg_sentence_length_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_sentence_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_avg_sentence_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_avg_shape_text_length_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_shape_text_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_avg_shape_text_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_avg_text_length_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_text_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_avg_text_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- Gnumeric ---

def test_gnumeric_all_sheets_have_data_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_all_sheets_have_data(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_all_sheets_have_data", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_string_length_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_avg_string_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_avg_string_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_cell_count_all_sheets_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cell_count_all_sheets(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cell_count_all_sheets", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
