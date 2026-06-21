"""
Dogfood pipeline: XCF remaining analytics + QOI remaining analytics → NDJSON export.
Covers XCF: xcf_aspect_ratio, xcf_canvas_perimeter, xcf_diagonal,
            xcf_file_size_kb, xcf_is_portrait, xcf_is_rgb
Covers QOI: qoi_cold_pixel_count, qoi_dark_pixel_count, qoi_has_warm_pixels,
            qoi_is_monochromatic, qoi_luminance_range, qoi_warm_pixel_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    xcf_aspect_ratio,
    xcf_canvas_perimeter,
    xcf_diagonal,
    xcf_file_size_kb,
    xcf_is_portrait,
    xcf_is_rgb,
)
from qoi.qoi_parser import (
    qoi_cold_pixel_count,
    qoi_dark_pixel_count,
    qoi_has_warm_pixels,
    qoi_is_monochromatic,
    qoi_luminance_range,
    qoi_warm_pixel_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


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


def test_xcf_canvas_perimeter_returns_int(tmp_path):
    path = _xcf_file()
    result = xcf_canvas_perimeter(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_canvas_perimeter", "perimeter": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["perimeter"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_diagonal_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_diagonal(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_diagonal", "diagonal": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["diagonal"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_file_size_kb_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_file_size_kb(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "xcf", "function": "xcf_file_size_kb", "kb": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["kb"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_xcf_is_portrait_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_portrait(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_portrait", "is_portrait": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_portrait"], bool)
    assert json.dumps(loaded[0]) is not None


def test_xcf_is_rgb_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_rgb(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_rgb", "is_rgb": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_rgb"], bool)
    assert json.dumps(loaded[0]) is not None


def test_qoi_cold_pixel_count_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_cold_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_cold_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_dark_pixel_count_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_dark_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_dark_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_has_warm_pixels_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_has_warm_pixels(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_has_warm_pixels", "has_warm": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_warm"], bool)
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_monochromatic_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_is_monochromatic(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_monochromatic", "is_mono": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_mono"], bool)
    assert json.dumps(loaded[0]) is not None


def test_qoi_luminance_range_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_luminance_range(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_luminance_range", "range": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_warm_pixel_count_returns_int(tmp_path):
    path = _qoi_file()
    result = qoi_warm_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_warm_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
