"""
Dogfood pipeline: XCF remaining analytics → NDJSON export.
Covers: get_capabilities, xcf_is_wide, xcf_pixel_density, xcf_layer_area_variance,
        xcf_pixel_count_per_layer, xcf_is_multi_layer
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import (
    get_capabilities,
    xcf_is_wide,
    xcf_pixel_density,
    xcf_layer_area_variance,
    xcf_pixel_count_per_layer,
    xcf_is_multi_layer,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _xcf_file():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_xcf_get_capabilities_returns_dict(tmp_path):
    result = get_capabilities()
    assert isinstance(result, dict)
    assert "format" in result
    assert result["format"] == "xcf"

    record = {"format": "xcf", "function": "get_capabilities", "format_name": result["format"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format_name"] == "xcf"
    assert json.dumps(loaded[0]) is not None


def test_xcf_is_wide_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_wide(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_wide", "is_wide": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_wide"], bool)
    assert json.dumps(loaded[0]) is not None


def test_xcf_pixel_density_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_pixel_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "xcf", "function": "xcf_pixel_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_area_variance_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_layer_area_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "xcf", "function": "xcf_layer_area_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_pixel_count_per_layer_returns_float(tmp_path):
    path = _xcf_file()
    result = xcf_pixel_count_per_layer(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "xcf", "function": "xcf_pixel_count_per_layer", "pixels_per_layer": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["pixels_per_layer"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_is_multi_layer_returns_bool(tmp_path):
    path = _xcf_file()
    result = xcf_is_multi_layer(path)
    assert isinstance(result, bool)

    record = {"format": "xcf", "function": "xcf_is_multi_layer", "is_multi_layer": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi_layer"], bool)
    assert json.dumps(loaded[0]) is not None
