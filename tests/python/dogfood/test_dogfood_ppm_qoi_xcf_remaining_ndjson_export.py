"""
Dogfood pipeline: PPM remaining + QOI remaining + XCF remaining → NDJSON export.
Covers PPM: ppm_megapixels, ppm_channel_balance
Covers QOI: probe_qoi, qoi_brightness_range, qoi_channel_balance
Covers XCF: xcf_layer_to_pixel_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_megapixels, ppm_channel_balance
from qoi.qoi_parser import probe_qoi, qoi_brightness_range, qoi_channel_balance
from xcf.xcf_parser import xcf_layer_to_pixel_ratio
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"


def _valid_ppm():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _valid_qoi():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def _valid_xcf():
    return str(next(iter(sorted(_XCF_DIR.glob("*.xcf")))))


def test_ppm_megapixels_returns_float(tmp_path):
    path = _valid_ppm()
    result = ppm_megapixels(path)
    assert isinstance(result, float)
    assert result > 0.0

    record = {"format": "ppm", "function": "ppm_megapixels", "megapixels": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["megapixels"] > 0.0
    assert json.dumps(loaded[0]) is not None


def test_ppm_channel_balance_returns_float(tmp_path):
    path = _valid_ppm()
    result = ppm_channel_balance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "ppm", "function": "ppm_channel_balance", "balance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["balance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_probe_qoi_returns_dict(tmp_path):
    path = _valid_qoi()
    result = probe_qoi(path)
    assert isinstance(result, dict)
    assert result.get("valid_header") is True
    assert result.get("width", 0) >= 1

    record = {"format": "qoi", "function": "probe_qoi", "valid": result.get("valid_header"), "width": result.get("width")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_qoi_brightness_range_returns_numeric(tmp_path):
    path = _valid_qoi()
    result = qoi_brightness_range(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "qoi", "function": "qoi_brightness_range", "range": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["range"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_qoi_channel_balance_returns_float(tmp_path):
    path = _valid_qoi()
    result = qoi_channel_balance(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "qoi", "function": "qoi_channel_balance", "balance": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["balance"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_xcf_layer_to_pixel_ratio_returns_float(tmp_path):
    path = _valid_xcf()
    result = xcf_layer_to_pixel_ratio(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "xcf", "function": "xcf_layer_to_pixel_ratio", "ratio": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0.0
    assert json.dumps(loaded[0]) is not None
