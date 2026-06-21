"""
Dogfood pipeline: FODG remaining + FODP remaining + ODT remaining + XCF remaining -> NDJSON export.
Covers FODG: fodg_unique_word_count, fodg_word_count
Covers FODP: fodp_chars_per_shape, fodp_has_multiple_slides, fodp_has_speaker_notes,
             fodp_slide_count_is_even, fodp_text_density_per_slide, fodp_total_chars_per_slide
Covers ODT: odt_digit_count, odt_space_count, odt_uppercase_ratio
Covers XCF: xcf_file_size_bytes
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import fodg_unique_word_count, fodg_word_count
from fodp.fodp_codec import (
    fodp_chars_per_shape,
    fodp_has_multiple_slides,
    fodp_has_speaker_notes,
    fodp_slide_count_is_even,
    fodp_text_density_per_slide,
    fodp_total_chars_per_slide,
)
from odt.odt_parser import odt_digit_count, odt_space_count, odt_uppercase_ratio
from xcf.xcf_parser import xcf_file_size_bytes
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _fodg_file():
    return str(next(iter(sorted(_FODG_DIR.glob("*.fodg")))))


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


# --- FODG ---

def test_fodg_unique_word_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_unique_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_unique_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_word_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODP ---

def test_fodp_chars_per_shape_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_chars_per_shape(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_chars_per_shape", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_has_multiple_slides_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_has_multiple_slides(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_has_multiple_slides", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_has_speaker_notes_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_has_speaker_notes(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_has_speaker_notes", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_slide_count_is_even_returns_bool(tmp_path):
    path = _fodp_file()
    result = fodp_slide_count_is_even(path)
    assert isinstance(result, bool)

    record = {"format": "fodp", "function": "fodp_slide_count_is_even", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodp_text_density_per_slide_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_text_density_per_slide(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_text_density_per_slide", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_total_chars_per_slide_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_total_chars_per_slide(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_total_chars_per_slide", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ODT ---

def test_odt_digit_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_digit_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_digit_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_space_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_space_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_space_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_uppercase_ratio_returns_float(tmp_path):
    path = _odt_file()
    result = odt_uppercase_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "odt", "function": "odt_uppercase_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- XCF ---

def test_xcf_file_size_bytes_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "xcf", "function": "xcf_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None
