"""
Dogfood pipeline: ODT remaining analytics + ODS remaining analytics → NDJSON export.
Covers ODT: odt_avg_chars_per_word, odt_avg_sentence_length, odt_has_numeric_content,
            odt_nonempty_paragraph_ratio, odt_nonspace_char_count, odt_total_text_length
Covers ODS: ods_is_rectangular, ods_is_single_cell, ods_is_single_row,
            ods_nonempty_cell_count, ods_nonempty_row_count, ods_nonempty_row_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import (
    odt_avg_chars_per_word,
    odt_avg_sentence_length,
    odt_has_numeric_content,
    odt_nonempty_paragraph_ratio,
    odt_nonspace_char_count,
    odt_total_text_length,
)
from ods.ods_analytics import ods_is_rectangular, ods_is_single_cell, ods_is_single_row, ods_nonempty_cell_count, ods_nonempty_row_count, ods_nonempty_row_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_odt_avg_chars_per_word_returns_float(tmp_path):
    path = _odt_file()
    result = odt_avg_chars_per_word(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_avg_chars_per_word", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_avg_sentence_length_returns_float(tmp_path):
    path = _odt_file()
    result = odt_avg_sentence_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_avg_sentence_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_has_numeric_content_returns_bool(tmp_path):
    path = _odt_file()
    result = odt_has_numeric_content(path)
    assert isinstance(result, bool)

    record = {"format": "odt", "function": "odt_has_numeric_content", "has_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_odt_nonempty_paragraph_ratio_returns_float(tmp_path):
    path = _odt_file()
    result = odt_nonempty_paragraph_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "odt", "function": "odt_nonempty_paragraph_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_odt_nonspace_char_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_nonspace_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_nonspace_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_total_text_length_returns_int(tmp_path):
    path = _odt_file()
    result = odt_total_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_total_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_is_rectangular_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_rectangular(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_rectangular", "is_rect": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_rect"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_is_single_cell_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_single_cell(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_single_cell", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_is_single_row_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_is_single_row(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_is_single_row", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_ods_nonempty_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_nonempty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_nonempty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_nonempty_row_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_nonempty_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_nonempty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_nonempty_row_ratio_returns_float(tmp_path):
    path = _ods_file()
    result = ods_nonempty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ods", "function": "ods_nonempty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None
