"""
Dogfood pipeline: PBM remaining + XCF remaining + QOI remaining -> NDJSON export.
Covers PBM: pbm_border_pixel_count, pbm_column_black_density, pbm_min_col_black_count,
            pbm_row_black_density, pbm_total_white_pixels
Covers XCF: xcf_layer_name_list, xcf_layer_width_sum, xcf_min_layer_area
Covers QOI: qoi_avg_brightness, qoi_channel_skew, qoi_green_dominance_ratio, qoi_is_single_pixel
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_border_pixel_count,
    pbm_column_black_density,
    pbm_min_col_black_count,
    pbm_row_black_density,
    pbm_total_white_pixels,
)
from xcf.xcf_parser import xcf_layer_name_list, xcf_layer_width_sum, xcf_min_layer_area
from qoi.qoi_parser import (
    qoi_avg_brightness,
    qoi_channel_skew,
    qoi_green_dominance_ratio,
    qoi_is_single_pixel,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


# --- PBM ---

def test_pbm_border_pixel_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_border_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_border_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_column_black_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_column_black_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_column_black_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_min_col_black_count_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_min_col_black_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_min_col_black_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_row_black_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_row_black_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_row_black_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_total_white_pixels_returns_int(tmp_path):
    path = _pbm_file()
    result = pbm_total_white_pixels(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_total_white_pixels", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- XCF ---

def test_xcf_layer_name_list_returns_list(tmp_path):
    path = _xcf_file()
    result = xcf_layer_name_list(path)
    assert isinstance(result, list)

    record = {"format": "xcf", "function": "xcf_layer_name_list", "names": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["names"], list)
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_width_sum_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_layer_width_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_layer_width_sum", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_min_layer_area_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_min_layer_area(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_min_layer_area", "area": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["area"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- QOI ---

def test_qoi_avg_brightness_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_avg_brightness(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_avg_brightness", "brightness": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["brightness"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_channel_skew_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_channel_skew(path)
    assert isinstance(result, (int, float))

    record = {"format": "qoi", "function": "qoi_channel_skew", "skew": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_qoi_green_dominance_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_green_dominance_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "qoi", "function": "qoi_green_dominance_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_single_pixel_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_is_single_pixel(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_single_pixel", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None
