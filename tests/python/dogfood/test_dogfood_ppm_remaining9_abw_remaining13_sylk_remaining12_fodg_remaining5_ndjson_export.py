"""
Dogfood pipeline: PPM remaining + ABW remaining + SYLK remaining + FODG remaining -> NDJSON export.
Covers PPM: ppm_pixel_brightness_sum, ppm_saturation_mean, ppm_width
Covers ABW: abw_chars_per_word, abw_has_multi_para
Covers SYLK: sylk_has_only_strings, sylk_value_length_variance
Covers FODG: fodg_has_multiple_shapes, fodg_is_empty_drawing, fodg_min_shape_count,
             fodg_shape_text_ratio, fodg_shapes_exceed_pages
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_pixel_brightness_sum, ppm_saturation_mean, ppm_width
from abw.abw_codec import abw_chars_per_word, abw_has_multi_para
from sylk.sylk_parser import sylk_has_only_strings, sylk_value_length_variance
from fodg.fodg_codec import (
    fodg_has_multiple_shapes,
    fodg_is_empty_drawing,
    fodg_min_shape_count,
    fodg_shape_text_ratio,
    fodg_shapes_exceed_pages,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _fodg_file():
    return str(next(iter(sorted(_FODG_DIR.glob("*.fodg")))))


# --- PPM ---

def test_ppm_pixel_brightness_sum_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_pixel_brightness_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_pixel_brightness_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_saturation_mean_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_saturation_mean(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_saturation_mean", "mean": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["mean"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_width_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_width(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "ppm", "function": "ppm_width", "width": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None


# --- ABW ---

def test_abw_chars_per_word_returns_float(tmp_path):
    path = _abw_file()
    result = abw_chars_per_word(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_chars_per_word", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_has_multi_para_returns_bool(tmp_path):
    path = _abw_file()
    result = abw_has_multi_para(path)
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "abw_has_multi_para", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- SYLK ---

def test_sylk_has_only_strings_returns_bool(tmp_path):
    path = _sylk_file()
    result = sylk_has_only_strings(path)
    assert isinstance(result, bool)

    record = {"format": "sylk", "function": "sylk_has_only_strings", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_value_length_variance_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_value_length_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_value_length_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODG ---

def test_fodg_has_multiple_shapes_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_has_multiple_shapes(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_has_multiple_shapes", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodg_is_empty_drawing_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_is_empty_drawing(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_is_empty_drawing", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodg_min_shape_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_min_shape_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_min_shape_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_shape_text_ratio_returns_float(tmp_path):
    path = _fodg_file()
    result = fodg_shape_text_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_shape_text_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_shapes_exceed_pages_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_shapes_exceed_pages(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_shapes_exceed_pages", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None
