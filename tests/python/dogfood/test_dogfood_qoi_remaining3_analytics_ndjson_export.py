"""
Dogfood pipeline: QOI remaining analytics → NDJSON export.
Covers: parse_qoi_strict, qoi_red_ratio, qoi_green_ratio, qoi_blue_ratio,
        qoi_pixel_density, qoi_is_dark
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    parse_qoi_strict,
    qoi_red_ratio,
    qoi_green_ratio,
    qoi_blue_ratio,
    qoi_pixel_density,
    qoi_is_dark,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"


def _qoi_file():
    return str(next(iter(sorted(_QOI_DIR.glob("*.qoi")))))


def test_qoi_parse_qoi_strict_returns_object(tmp_path):
    path = _qoi_file()
    result = parse_qoi_strict(path)
    assert result is not None
    assert result.width >= 1
    assert result.height >= 1

    record = {"format": "qoi", "function": "parse_qoi_strict", "width": result.width, "height": result.height}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_qoi_red_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_red_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "qoi", "function": "qoi_red_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_green_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_green_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "qoi", "function": "qoi_green_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_blue_ratio_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_blue_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "qoi", "function": "qoi_blue_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_pixel_density_returns_float(tmp_path):
    path = _qoi_file()
    result = qoi_pixel_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "qoi", "function": "qoi_pixel_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_qoi_is_dark_returns_bool(tmp_path):
    path = _qoi_file()
    result = qoi_is_dark(path)
    assert isinstance(result, bool)

    record = {"format": "qoi", "function": "qoi_is_dark", "is_dark": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_dark"], bool)
    assert json.dumps(loaded[0]) is not None
