"""
Dogfood pipeline: FODP remaining + PPM remaining + XCF remaining -> NDJSON export.
Covers FODP: fodp_avg_slide_shape_count, fodp_max_word_count_per_slide, fodp_total_word_count
Covers PPM: ppm_avg_channel_diff, ppm_avg_green_channel, ppm_blue_dominant_count,
            ppm_green_dominant_count, ppm_total_green_sum
Covers XCF: xcf_color_depth, xcf_layer_pixel_count, xcf_total_pixel_count, xcf_width_plus_height
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_avg_slide_shape_count, fodp_max_word_count_per_slide, fodp_total_word_count
from ppm.ppm_parser import (
    ppm_avg_channel_diff,
    ppm_avg_green_channel,
    ppm_blue_dominant_count,
    ppm_green_dominant_count,
    ppm_total_green_sum,
)
from xcf.xcf_parser import (
    xcf_color_depth,
    xcf_layer_pixel_count,
    xcf_total_pixel_count,
    xcf_width_plus_height,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _fodp_file():
    return str(next(iter(sorted(_FODP_DIR.glob("*.fodp")))))


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_fodp_avg_slide_shape_count_returns_float(tmp_path):
    path = _fodp_file()
    result = fodp_avg_slide_shape_count(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_avg_slide_shape_count", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_max_word_count_per_slide_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_max_word_count_per_slide(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_max_word_count_per_slide", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodp_total_word_count_returns_int(tmp_path):
    path = _fodp_file()
    result = fodp_total_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodp", "function": "fodp_total_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_avg_channel_diff_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_avg_channel_diff(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_avg_channel_diff", "diff": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["diff"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_avg_green_channel_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_avg_green_channel(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_avg_green_channel", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_blue_dominant_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_blue_dominant_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_blue_dominant_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_green_dominant_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_green_dominant_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_green_dominant_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_total_green_sum_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_total_green_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_total_green_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_color_depth_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_color_depth(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_color_depth", "depth": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["depth"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_pixel_count_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_layer_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_layer_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_total_pixel_count_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_total_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_total_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_width_plus_height_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_width_plus_height(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_width_plus_height", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None
