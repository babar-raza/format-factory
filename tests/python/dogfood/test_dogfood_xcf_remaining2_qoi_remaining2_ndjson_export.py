"""
Dogfood pipeline: XCF remaining analytics + QOI remaining analytics → NDJSON export.
Covers XCF: parse_xcf_strict, xcf_is_multi_pixel, xcf_row_count, xcf_file_bytes_per_layer,
            xcf_file_size_per_pixel, xcf_layer_size_variance
Covers QOI: qoi_color_depth_estimate, qoi_is_bright, qoi_saturation_estimate,
            qoi_pixel_contrast, qoi_channel_variance, qoi_red_blue_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    parse_xcf_strict,
    xcf_is_multi_pixel,
    xcf_row_count,
    xcf_file_bytes_per_layer,
    xcf_file_size_per_pixel,
    xcf_layer_size_variance,
)
from qoi.qoi_parser import (
    qoi_color_depth_estimate,
    qoi_is_bright,
    qoi_saturation_estimate,
    qoi_pixel_contrast,
    qoi_channel_variance,
    qoi_red_blue_ratio,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def test_xcf_parse_strict_returns_image(tmp_path):
    path = _xcf_file()
    result = parse_xcf_strict(path)
    assert hasattr(result, "width")
    assert hasattr(result, "height")
    assert result.width > 0

    record = {"format": "xcf", "function": "parse_xcf_strict", "width": result.width, "height": result.height}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] > 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_is_multi_pixel_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_multi_pixel(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_multi_pixel", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None


def test_xcf_row_count_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_file_bytes_per_layer_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_file_bytes_per_layer(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_file_bytes_per_layer", "bytes": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["bytes"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_file_size_per_pixel_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_file_size_per_pixel(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_file_size_per_pixel", "size": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_size_variance_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_layer_size_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_layer_size_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_color_depth_estimate_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_color_depth_estimate(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_color_depth_estimate", "estimate": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["estimate"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_bright_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_is_bright(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_bright", "is_bright": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_bright"], bool)
    assert json.dumps(loaded[0]) is not None


def test_qoi_saturation_estimate_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_saturation_estimate(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_saturation_estimate", "saturation": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["saturation"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_pixel_contrast_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_pixel_contrast(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_pixel_contrast", "contrast": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["contrast"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_channel_variance_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_channel_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_channel_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_red_blue_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_red_blue_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_red_blue_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None
