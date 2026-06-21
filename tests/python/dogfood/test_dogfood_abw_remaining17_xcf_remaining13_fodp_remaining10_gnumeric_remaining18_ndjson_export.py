"""
Dogfood pipeline: ABW remaining + XCF remaining + FODP remaining + Gnumeric remaining -> NDJSON export.
Covers ABW: abw_has_numeric_content, abw_has_unicode, abw_is_single_paragraph
Covers XCF: xcf_file_header_overhead, xcf_has_multiple_layers, xcf_height_squared
Covers FODP: fodp_file_size_bytes, fodp_has_multi_slide, fodp_has_numeric_content
Covers Gnumeric: gnumeric_cells_exceed_rows, gnumeric_col_span, gnumeric_column_count_file
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_has_numeric_content, abw_has_unicode, abw_is_single_paragraph
from xcf.xcf_parser import xcf_file_header_overhead, xcf_has_multiple_layers, xcf_height_squared
from fodp.fodp_codec import fodp_file_size_bytes, fodp_has_multi_slide, fodp_has_numeric_content
from gnumeric.gnumeric_codec import gnumeric_cells_exceed_rows, gnumeric_col_span, gnumeric_column_count_file
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

def test_abw_has_numeric_content_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_has_numeric_content(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_numeric_content", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_has_unicode_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_has_unicode(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_unicode", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_is_single_paragraph_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_is_single_paragraph(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_is_single_paragraph", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- XCF ---

def test_xcf_file_header_overhead_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_file_header_overhead(path)
    assert isinstance(result, int)

    record = {"format": "xcf", "function": "xcf_file_header_overhead", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], int)
    assert json.dumps(loaded[0]) is not None


def test_xcf_has_multiple_layers_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_has_multiple_layers(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_has_multiple_layers", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_xcf_height_squared_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_height_squared(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_height_squared", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODP ---

def test_fodp_file_size_bytes_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "fodp", "function": "fodp_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_has_multi_slide_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_has_multi_slide(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_has_multi_slide", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_has_numeric_content_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_has_numeric_content(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_has_numeric_content", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- Gnumeric ---

def test_gnumeric_cells_exceed_rows_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cells_exceed_rows(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_cells_exceed_rows", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_col_span_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_col_span(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_col_span", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_column_count_file_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_column_count_file(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_column_count_file", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
