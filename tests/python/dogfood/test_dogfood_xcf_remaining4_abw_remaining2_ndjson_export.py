"""
Dogfood pipeline: XCF remaining analytics + ABW remaining analytics → NDJSON export.
Covers XCF: xcf_is_square, xcf_layer_area_sum, xcf_layer_density,
            xcf_megapixel_count, xcf_perimeter, xcf_width_to_height_ratio
Covers ABW: abw_avg_paragraph_words, abw_avg_sentence_length, abw_avg_word_length_per_para,
            abw_has_multiple_paragraphs, abw_max_paragraph_word_count, abw_section_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    xcf_is_square,
    xcf_layer_area_sum,
    xcf_layer_density,
    xcf_megapixel_count,
    xcf_perimeter,
    xcf_width_to_height_ratio,
)
from abw.abw_codec import (
    abw_avg_paragraph_words,
    abw_avg_sentence_length,
    abw_avg_word_length_per_para,
    abw_has_multiple_paragraphs,
    abw_max_paragraph_word_count,
    abw_section_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_ABW_FILE = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_xcf_is_square_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_square(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_square", "is_square": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_square"], bool)
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_area_sum_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_layer_area_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_layer_area_sum", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_density_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_layer_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_layer_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_megapixel_count_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_megapixel_count(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_megapixel_count", "mp": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mp"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_perimeter_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_perimeter(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_perimeter", "perimeter": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["perimeter"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_width_to_height_ratio_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_width_to_height_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_width_to_height_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_paragraph_words_returns_float(tmp_path):
    path = str(_ABW_FILE)
    result = abw_avg_paragraph_words(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_paragraph_words", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_sentence_length_returns_float(tmp_path):
    path = str(_ABW_FILE)
    result = abw_avg_sentence_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_sentence_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_avg_word_length_per_para_returns_float(tmp_path):
    path = str(_ABW_FILE)
    result = abw_avg_word_length_per_para(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_word_length_per_para", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_multiple_paragraphs_returns_bool(tmp_path):
    path = str(_ABW_FILE)
    result = abw_has_multiple_paragraphs(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_multiple_paragraphs", "has_multiple": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_multiple"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_max_paragraph_word_count_returns_int(tmp_path):
    path = str(_ABW_FILE)
    result = abw_max_paragraph_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_max_paragraph_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_section_count_returns_int(tmp_path):
    path = str(_ABW_FILE)
    result = abw_section_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "abw_section_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
